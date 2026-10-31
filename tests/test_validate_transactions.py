from src.validate_transactions import validate_transactions


def create_valid_transaction():
    """Create one valid debit-credit transaction pair."""

    debit = {
        "transaction_id": "TXN001",
        "leg_id": "TXN001_D",
        "account_id": "ACC001",
        "counterparty_account_id": "ACC002",
        "leg_type": "DEBIT",
        "amount": "100.00",
        "currency": "INR",
        "event_timestamp": "2026-01-01T10:00:00+00:00",
        "event_sequence": 1,
        "reference_id": "REF001"
    }

    credit = {
        "transaction_id": "TXN001",
        "leg_id": "TXN001_C",
        "account_id": "ACC002",
        "counterparty_account_id": "ACC001",
        "leg_type": "CREDIT",
        "amount": "100.00",
        "currency": "INR",
        "event_timestamp": "2026-01-01T10:00:01+00:00",
        "event_sequence": 2,
        "reference_id": "REF001"
    }

    return [debit, credit]


def test_valid_transaction_is_accepted():
    records = create_valid_transaction()

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 2
    assert len(rejected) == 0


def test_unbalanced_transaction_is_rejected():
    records = create_valid_transaction()
    records[1]["amount"] = "150.00"

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert any(
        "Debit and credit amounts do not balance." in item["errors"]
        for item in rejected
    )


def test_missing_account_id_is_rejected():
    records = create_valid_transaction()
    records[0]["account_id"] = None

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert any(
        "Missing required field: account_id" in item["errors"]
        for item in rejected
    )

    assert any(
        "Debit and credit account references do not match." in item["errors"]
        for item in rejected
    )


def test_duplicate_leg_id_is_rejected():
    records = create_valid_transaction()
    records[1]["leg_id"] = records[0]["leg_id"]

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert all(
        "Duplicate leg_id." in item["errors"]
        for item in rejected
    )


def test_invalid_amount_is_rejected():
    records = create_valid_transaction()
    records[0]["amount"] = "-50"

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2


def test_currency_mismatch_is_rejected():
    records = create_valid_transaction()
    records[1]["currency"] = "USD"

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert any(
        "Debit and credit currencies do not match." in item["errors"]
        for item in rejected
    )


def test_invalid_event_sequence_is_rejected():
    records = create_valid_transaction()
    records[1]["event_sequence"] = 1

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert any(
        "Invalid event sequence ordering." in item["errors"]
        for item in rejected
    )


def test_out_of_order_timestamp_is_rejected():
    records = create_valid_transaction()

    # Debit occurs after the credit.
    records[0]["event_timestamp"] = "2026-01-01T10:00:05+00:00"

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 2

    assert any(
        "Debit event occurs after credit event." in item["errors"]
        for item in rejected
    )


def test_incomplete_transaction_is_rejected():
    records = create_valid_transaction()
    records.pop()

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 0
    assert len(rejected) == 1

    assert any(
        "Transaction must contain exactly two legs." in item["errors"]
        for item in rejected
    )


def test_malformed_record_is_rejected():
    records = create_valid_transaction()
    records.append("invalid_record")

    accepted, rejected = validate_transactions(records)

    assert len(accepted) == 2
    assert len(rejected) == 1

    assert "Record must be a JSON object." in rejected[0]["errors"]


def test_empty_input():
    accepted, rejected = validate_transactions([])

    assert accepted == []
    assert rejected == []


def test_unexpected_extra_field_is_tolerated():
    records = create_valid_transaction()
    records[0]["new_source_field"] = "EXTRA_VALUE"

    accepted, rejected = validate_transactions(records)

    # Current validator permits additional fields.
    assert len(accepted) == 2
    assert len(rejected) == 0


def test_reconciliation():
    records = create_valid_transaction()
    records[0]["amount"] = "200"

    accepted, rejected = validate_transactions(records)

    assert len(records) == len(accepted) + len(rejected)