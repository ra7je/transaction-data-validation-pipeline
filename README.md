# Bank Transaction Data Pipeline

## About the Project

I built this project to process and validate bank transaction data using Python, Snowflake and dbt.

The main goal is to make sure that every transaction has the correct debit and credit entries before it is published. The pipeline also identifies duplicate records, invalid transactions and data quality issues.

I wanted to build a complete data pipeline that covers everything from generating sample data to ingestion, transformation, validation and reconciliation.

## Technologies Used

- Python
- Snowflake
- SQL
- dbt
- Pytest

## How the Pipeline Works

The project follows a Bronze, Silver and Gold architecture.

**Bronze Layer – Raw Data**

I use Python to generate synthetic transaction records in JSON format. These files are uploaded to a Snowflake internal stage and loaded into the Bronze table using `COPY INTO`.

The original data is stored in VARIANT format so that the raw input is preserved.

**Silver Layer – Data Cleaning**

In this layer, I extract individual transaction records from the JSON data using `LATERAL FLATTEN`.

I standardize the fields, convert data types and identify duplicate transaction leg IDs.

**Gold Layer – Validated Data**

The Gold layer contains the final results:

- Valid transactions
- Rejected transaction records with rejection reasons
- Transaction reconciliation results
- Pipeline audit information

Only transactions that satisfy the validation rules are published as accepted records.

## Data Quality Checks

I implemented checks for:

- Missing transaction IDs and account details
- Duplicate transaction leg IDs
- Invalid transaction types
- Zero or negative transaction amounts
- Invalid currencies
- Missing or invalid timestamps
- Incorrect event sequences
- Missing debit or credit entries
- Debit and credit amount mismatches
- Currency inconsistencies
- Incorrect event ordering

Rejected records are retained with their rejection reasons so they can be investigated later.

## Backfill and Failure Handling

I tested the pipeline with a separate backfill batch containing 100 transaction legs.

I also executed the same Snowflake ingestion command again to check whether previously loaded files would be inserted a second time. Snowflake skipped the files that had already been loaded.

To test failure handling, I uploaded a JSON file with invalid syntax. Snowflake detected the parsing error and loaded zero rows from that file.

## Testing

I used Pytest to test the Python validation logic.

Run the tests from the project root:

```bash
python -m pytest -v
```

**Last verified result:** 13 tests passed.

I also used dbt to run the transformation models and data quality tests.

Run from the `dbt_transaction_pipeline` directory:

```bash
dbt build
```

**Last verified result:**
- 5 models processed
- 11 dbt tests passed
- 6 seeds processed
- 22 out of 22 operations successful

## Performance Testing

I generated a separate dataset containing 10,000 transaction legs to test the pipeline with a larger volume of data.

The observed results were:

| Measurement | Result |
|---|---:|
| Input records | 10,000 |
| Snowflake file load | Approximately 1.1 seconds |
| dbt build | 7.2 seconds |
| Successful dbt operations | 22/22 |

These timings are based on my test environment.

## Final Results

After loading the original data, backfill batch and performance batch, I checked the final counts using the Snowflake audit table.

| Metric | Records |
|---|---:|
| Raw documents | 3 |
| Raw transaction legs | 10,129 |
| Silver records | 10,129 |
| Accepted transaction legs | 10,114 |
| Accepted transactions | 5,057 |
| Rejected records | 14 |
| Duplicate records | 1 |
| Unaccounted records | 0 |

The records reconcile as follows:

```text
10,129 = 10,114 + 14 + 1
```

Both ingestion and publication statuses showed `RECONCILED`.

## How to Run the Project

Generate transaction records from the project root:

```bash
python generate_transactions.py --records 1000
```

Run Python tests:

```bash
python -m pytest -v
```

Run dbt from the `dbt_transaction_pipeline` directory:

```bash
dbt build
```

Snowflake connection details should be configured locally. Passwords and other sensitive credentials should never be committed to GitHub.

## Future Improvements

- Add automated schema-change detection.
- Introduce scheduled data ingestion.
- Improve monitoring and error notifications.
- Test with larger datasets.
- Add automated testing through CI/CD.

## Conclusion

Building this project gave me practical experience with the complete data engineering workflow, including data generation, Snowflake ingestion, dbt transformations, data quality checks, backfill processing, failure handling and reconciliation.