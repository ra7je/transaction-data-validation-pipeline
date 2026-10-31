# Data Dictionary

## 1. Overview

This document describes the fields used in the bank transaction pipeline, including their purpose and how they are used during data processing and validation.

Each transaction is represented by two entries: a debit leg and a credit leg.

## 2. Transaction Fields

| Field | Data Type | Description |
|---|---|---|
| `transaction_id` | VARCHAR | Unique identifier used to group the debit and credit entries belonging to a transaction |
| `leg_id` | VARCHAR | Unique identifier for an individual transaction leg |
| `account_id` | VARCHAR | Account associated with the current transaction leg |
| `counterparty_account_id` | VARCHAR | Account on the other side of the transaction |
| `leg_type` | VARCHAR | Identifies whether the entry is a DEBIT or CREDIT |
| `amount` | DECIMAL(18,2) | Transaction amount |
| `currency` | VARCHAR | Currency used for the transaction, such as INR or USD |
| `event_timestamp` | TIMESTAMP | Date and time when the transaction event occurred |
| `event_sequence` | NUMBER | Sequence number used to identify the order of transaction events |
| `reference_id` | VARCHAR | Reference identifier associated with the transaction |

## 3. Bronze Layer Fields

| Field | Data Type | Description |
|---|---|---|
| `RAW_RECORD` | VARIANT | Original JSON transaction data loaded into Snowflake |
| `SOURCE_FILE` | VARCHAR | Name of the file from which the data was loaded |
| `INGESTED_AT` | TIMESTAMP_NTZ | Timestamp when the raw record was ingested |

## 4. Silver Layer Fields

The Silver model extracts transaction legs from the raw JSON and standardizes their values.

It contains the transaction fields described above, along with:

| Field | Data Type | Description |
|---|---|---|
| `DUPLICATE_RANK` | NUMBER | Ranking used to identify repeated leg IDs |
| `IS_DUPLICATE` | BOOLEAN | Indicates whether the transaction leg is identified as a duplicate |

## 5. Gold Layer Outputs

### FACT_VALID_TRANSACTIONS

Contains the transaction legs that pass the validation conditions and belong to balanced transactions.

### REJECTED_TRANSACTION_LEGS

Contains records that fail validation, along with a rejection reason explaining why they were excluded.

### TRANSACTION_RECONCILIATION

Contains transaction-level checks, including:

- Number of transaction legs
- Debit and credit totals
- Currency consistency
- Balance status

### PIPELINE_AUDIT

Tracks the pipeline's record counts and reconciliation status across the processing layers.

## 6. Validation Expectations

The pipeline uses the following expectations:

- Each transaction should contain one debit and one credit entry.
- Debit and credit amounts should match.
- Transaction identifiers and leg identifiers should be present.
- Account details should be available.
- Amounts should be positive.
- Currency should be valid.
- Event timestamps and sequences should be available.
- Duplicate leg IDs should not be published as accepted records.

## 7. Data Handling

Raw input is preserved in the Bronze layer.

Cleaned transaction records are maintained in Silver.

Validated records and rejection details are published in Gold.

This separation helps trace a transaction from its original input to its final processing result.