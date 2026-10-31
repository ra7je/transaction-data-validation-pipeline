
import json
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "data" / "generated" / "transactions.json"
OUTPUT_DIR = BASE_DIR / "data" / "validated"

VALID_CURRENCIES = {"INR", "USD"}
VALID_LEG_TYPES = {"DEBIT", "CREDIT"}

REQUIRED_FIELDS = [
    "transaction_id",
    "leg_id",
    "account_id",
    "counterparty_account_id",
    "leg_type",
    "amount",
    "currency",
    "event_timestamp",
    "event_sequence",
    "reference_id",
]


def load_transactions(file_path):
    """Load transaction records from a JSON file."""
    with file_path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Input JSON must contain a list of records.")

    return records


def validate_transactions(records):
    """Validate individual transaction legs and transaction pairs."""

    errors = defaultdict(list)
    leg_ids = [
        record.get("leg_id")
        for record in records
        if isinstance(record, dict) and record.get("leg_id")
    ]
    duplicate_leg_ids = {
        key for key, count in Counter(leg_ids).items() if count > 1
    }

    transaction_groups = defaultdict(list)

    # Individual record validation
    for index, record in enumerate(records):

        if not isinstance(record, dict):
            errors[index].append("Record must be a JSON object.")
            continue

        for field in REQUIRED_FIELDS:
            if field not in record or record[field] is None or record[field] == "":
                errors[index].append(f"Missing required field: {field}")

        leg_id = record.get("leg_id")
        if leg_id in duplicate_leg_ids:
            errors[index].append("Duplicate leg_id.")

        if record.get("leg_type") not in VALID_LEG_TYPES:
            errors[index].append("Invalid leg_type.")

        if record.get("currency") not in VALID_CURRENCIES:
            errors[index].append("Unsupported currency.")

        try:
            amount = Decimal(str(record.get("amount")))
            if not amount.is_finite() or amount <= 0:
                errors[index].append("Amount must be greater than zero.")
        except (InvalidOperation, TypeError, ValueError):
            errors[index].append("Amount must be a valid decimal number.")

        try:
            datetime.fromisoformat(record.get("event_timestamp"))
        except (ValueError, TypeError):
            errors[index].append("Invalid event_timestamp.")

        try:
            if int(record.get("event_sequence")) <= 0:
                errors[index].append("event_sequence must be positive.")
        except (ValueError, TypeError):
            errors[index].append("Invalid event_sequence.")

        if record.get("transaction_id"):
            transaction_groups[record["transaction_id"]].append(index)

    # Transaction-level validation
    for transaction_id, indexes in transaction_groups.items():

        if len(indexes) != 2:
            for index in indexes:
                errors[index].append(
                    "Transaction must contain exactly two legs."
                )
            continue

        debit_records = [
            records[i] for i in indexes
            if records[i].get("leg_type") == "DEBIT"
        ]
        credit_records = [
            records[i] for i in indexes
            if records[i].get("leg_type") == "CREDIT"
        ]

        if len(debit_records) != 1 or len(credit_records) != 1:
            for index in indexes:
                errors[index].append(
                    "Transaction must have one DEBIT and one CREDIT leg."
                )
            continue

        debit = debit_records[0]
        credit = credit_records[0]

        try:
            if Decimal(str(debit["amount"])) != Decimal(str(credit["amount"])):
                raise ValueError
        except (ValueError, InvalidOperation, KeyError, TypeError):
            for index in indexes:
                errors[index].append("Debit and credit amounts do not balance.")

        if debit.get("currency") != credit.get("currency"):
            for index in indexes:
                errors[index].append("Debit and credit currencies do not match.")

        if debit.get("account_id") != credit.get("counterparty_account_id"):
            for index in indexes:
                errors[index].append("Debit and credit account references do not match.")

        if credit.get("account_id") != debit.get("counterparty_account_id"):
            for index in indexes:
                errors[index].append("Counterparty account references do not match.")

        try:
            debit_time = datetime.fromisoformat(debit["event_timestamp"])
            credit_time = datetime.fromisoformat(credit["event_timestamp"])

            if debit_time > credit_time:
                for index in indexes:
                    errors[index].append("Debit event occurs after credit event.")

            if int(debit["event_sequence"]) >= int(credit["event_sequence"]):
                for index in indexes:
                    errors[index].append("Invalid event sequence ordering.")

        except (ValueError, TypeError, KeyError):
            pass

        if debit.get("reference_id") != credit.get("reference_id"):
            for index in indexes:
                errors[index].append("Reference IDs do not match.")

    accepted = []
    rejected = []

    for index, record in enumerate(records):
        if errors[index]:
            rejected.append({
                "record": record,
                "errors": sorted(set(errors[index]))
            })
        else:
            accepted.append(record)

    return accepted, rejected


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records = load_transactions(INPUT_FILE)
    accepted, rejected = validate_transactions(records)

    accepted_file = OUTPUT_DIR / "accepted_transactions.json"
    rejected_file = OUTPUT_DIR / "rejected_transactions.json"

    with accepted_file.open("w", encoding="utf-8") as file:
        json.dump(accepted, file, indent=2)

    with rejected_file.open("w", encoding="utf-8") as file:
        json.dump(rejected, file, indent=2)

    print("TRANSACTION VALIDATION SUMMARY")
    print("--------------------------------")
    print(f"Input records:    {len(records)}")
    print(f"Accepted records: {len(accepted)}")
    print(f"Rejected records: {len(rejected)}")
    print(f"Reconciliation:   {len(records) == len(accepted) + len(rejected)}")
    print(f"\nAccepted file: {accepted_file}")
    print(f"Rejected file: {rejected_file}")


if __name__ == "__main__":
    main()
