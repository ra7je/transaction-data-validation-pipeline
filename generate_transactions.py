
import json
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta, timezone
from decimal import Decimal


SEED = 42
CURRENCIES = ["INR", "USD"]
ACCOUNT_COUNT = 100


def generate_transactions(record_count, batch_id=None):
    random.seed(SEED)

    accounts = [
        f"ACC{i:04d}"
        for i in range(1, ACCOUNT_COUNT + 1)
    ]

    transactions = []
    transaction_count = (record_count + 1) // 2
    start_time = datetime(2026, 1, 1, tzinfo=timezone.utc)

    prefix = f"{batch_id}_" if batch_id else ""

    for i in range(transaction_count):
        txn_id = f"{prefix}TXN{i + 1:07d}"
        reference_id = f"{prefix}REF{i + 1:07d}"

        debit_account, credit_account = random.sample(accounts, 2)
        amount = Decimal(random.randint(100, 100000)) / 100
        currency = random.choice(CURRENCIES)

        event_time = start_time + timedelta(seconds=i * 2)

        debit = {
            "transaction_id": txn_id,
            "leg_id": f"{txn_id}_D",
            "account_id": debit_account,
            "counterparty_account_id": credit_account,
            "leg_type": "DEBIT",
            "amount": str(amount),
            "currency": currency,
            "event_timestamp": event_time.isoformat(),
            "event_sequence": 1,
            "reference_id": reference_id
        }

        credit = {
            "transaction_id": txn_id,
            "leg_id": f"{txn_id}_C",
            "account_id": credit_account,
            "counterparty_account_id": debit_account,
            "leg_type": "CREDIT",
            "amount": str(amount),
            "currency": currency,
            "event_timestamp": (
                event_time + timedelta(seconds=1)
            ).isoformat(),
            "event_sequence": 2,
            "reference_id": reference_id
        }

        transactions.extend([debit, credit])

    return transactions[:record_count]


def generate_invalid_transactions(batch_id=None):
    invalid = generate_transactions(18, batch_id)

    for record in invalid:
        record["transaction_id"] = "BAD_" + record["transaction_id"]
        record["leg_id"] = "BAD_" + record["leg_id"]
        record["reference_id"] = "BAD_" + record["reference_id"]

    # 1. Unbalanced debit and credit
    invalid[1]["amount"] = "99999.99"

    # 2. Duplicate leg ID
    duplicate = invalid[2].copy()
    invalid.append(duplicate)

    # 3. Missing account ID
    invalid[4]["account_id"] = ""

    # 4. Null transaction ID
    invalid[6]["transaction_id"] = None

    # 5. Invalid currency
    invalid[8]["currency"] = "XYZ"

    # 6. Zero amount
    invalid[10]["amount"] = "0.00"

    # 7. Negative amount
    invalid[12]["amount"] = "-250.00"

    # 8. Invalid leg type
    invalid[14]["leg_type"] = "TRANSFER"

    # 9. Out-of-order event timestamp
    invalid[17]["event_timestamp"] = (
        "2025-12-31T00:00:00+00:00"
    )

    return invalid


def save_transactions(records, output_path):
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)

    print(f"Generated records: {len(records)}")
    print(f"Output file: {output.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic bank transactions"
    )

    parser.add_argument(
        "--records",
        type=int,
        default=1000,
        help="Number of transaction legs"
    )

    parser.add_argument(
        "--output",
        default="data/generated/transactions.json",
        help="Output JSON file path"
    )

    parser.add_argument(
        "--include-invalid",
        action="store_true",
        help="Add invalid test scenarios"
    )

    parser.add_argument(
        "--batch-id",
        type=str,
        default=None,
        help="Optional unique batch identifier for backfill"
    )

    args = parser.parse_args()

    if args.records <= 0:
        parser.error("--records must be greater than zero")

    if args.batch_id and not all(
        char.isalnum() or char == "_"
        for char in args.batch_id
    ):
        parser.error("--batch-id can contain only letters, numbers and underscores")

    records = generate_transactions(
        args.records,
        args.batch_id
    )

    if args.include_invalid:
        records.extend(
            generate_invalid_transactions(args.batch_id)
        )

    save_transactions(records, args.output)


if __name__ == "__main__":
    main()
