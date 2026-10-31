# Testing and Performance Report

## 1. Overview

I tested the pipeline at different stages to check whether transaction records are generated, ingested, validated and published correctly.

I used Pytest for Python validation tests, dbt tests for transformed data and Snowflake queries to verify ingestion and reconciliation.

## 2. Python Unit Testing

I created unit tests for the Python transaction validation logic.

The tests cover:

- Valid transactions
- Unbalanced debit and credit amounts
- Missing account details
- Duplicate leg IDs
- Invalid amounts
- Currency mismatches
- Invalid event sequences
- Incorrect event timestamps
- Incomplete transactions
- Malformed records
- Empty input
- Unexpected additional fields
- Reconciliation of accepted and rejected records

**Last verified result: 13 tests passed.**

Command:

```bash
python -m pytest -v
```

## 3. dbt Testing

I used dbt to execute the transformation models and data quality tests.

Command:

```bash
dbt build
```

Last verified result:

| Item | Result |
|---|---:|
| Models | 5 |
| Tests | 11 |
| Seeds | 6 |
| Successful operations | 22 |
| Failed operations | 0 |

## 4. Backfill Testing

I generated a separate batch named `BACKFILL_001`, containing 100 transaction legs.

I uploaded the file to the existing Snowflake stage and executed the ingestion command.

The new records were processed along with the original dataset.

## 5. Idempotency Testing

I executed the same Snowflake `COPY INTO` command again after loading the original and backfill files.

Snowflake reported zero files processed because those files had already been loaded.

This verified repeated staged-file ingestion behaviour.

## 6. Failure Handling Testing

I created a JSON file with invalid syntax and uploaded it to the Snowflake stage.

The load command used:

```sql
ON_ERROR = 'ABORT_STATEMENT';
```

Snowflake detected the JSON parsing error and loaded zero rows from the malformed file.

I then removed the invalid test file from the stage.

## 7. Performance Testing

I generated a separate performance dataset containing 10,000 transaction legs, representing 5,000 debit-credit transactions.

The file was uploaded and loaded into Snowflake.

Observed results:

| Measurement | Result |
|---|---:|
| Input transaction legs | 10,000 |
| Snowflake file load | Approximately 1.1 seconds |
| dbt build | 7.2 seconds |
| Successful dbt operations | 22/22 |

These results were observed in the tested environment and are not production performance guarantees.

## 8. Final Reconciliation

After loading all three valid input files, I checked the pipeline audit results in Snowflake.

| Metric | Result |
|---|---:|
| Raw documents | 3 |
| Raw transaction legs | 10,129 |
| Silver records | 10,129 |
| Accepted transaction legs | 10,114 |
| Accepted transactions | 5,057 |
| Rejected records | 14 |
| Duplicate records | 1 |
| Unaccounted records | 0 |

The record counts reconcile:

```text
10,129 = 10,114 + 14 + 1
```

Both ingestion and publication statuses showed `RECONCILED`.

## 9. Test Summary

The tests demonstrated the following:

- Python validation logic passed its 13 unit tests.
- dbt completed all 22 operations successfully.
- A separate backfill batch was ingested.
- Repeated ingestion skipped previously loaded files.
- Malformed JSON was rejected.
- Final pipeline counts reconciled successfully.

## 10. Future Testing

Further testing can include:

- Larger datasets to evaluate performance at higher volumes.
- Schema-change detection.
- Automated retry and restart scenarios.
- Concurrent ingestion.
- Automated CI/CD testing.

## 11. Conclusion

The testing process helped me verify the main pipeline functionality, data quality rules, repeated file ingestion, failure handling and reconciliation.

The results provide evidence that the current implementation works for the tested datasets and scenarios.