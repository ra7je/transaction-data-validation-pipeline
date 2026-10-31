# Design Decisions

## 1. Project Approach

I wanted to build a pipeline that handles the complete transaction data flow rather than only performing data transformations.

I focused on data quality, traceability, reconciliation, safe reruns and handling different input scenarios.

## 2. Technology Choices

### Python

I chose Python for generating synthetic transaction data and implementing validation logic.

It also helped me create repeatable test scenarios, including valid transactions, duplicates and invalid records.

### Snowflake

I used Snowflake as the data warehouse because it supports structured and semi-structured data.

The VARIANT data type allows me to preserve the original JSON input, while SQL provides the processing capabilities needed for the pipeline.

### dbt

I used dbt to organize SQL transformations into separate models.

This keeps the processing logic manageable and allows me to execute data quality tests along with the models.

### Pytest

I used Pytest to test the Python validation logic independently.

This helped me check different transaction scenarios without depending on a Snowflake execution for every test.

## 3. Layered Architecture

I separated the pipeline into Bronze, Silver and Gold layers.

- Bronze preserves the original input.
- Silver handles extraction, cleaning and standardization.
- Gold contains accepted records, rejected records and reconciliation outputs.

This makes the processing flow easier to understand and troubleshoot.

## 4. Data Quality Decisions

I treated transaction validation as a combination of record-level and transaction-level checks.

Record-level checks identify problems such as missing fields, invalid amounts and duplicate leg IDs.

Transaction-level checks verify that debit and credit entries are present, their amounts match and their currencies are consistent.

This distinction is important because an individual record can look valid while the complete transaction is incorrect.

## 5. Rejected Records

I decided to retain rejected records with their rejection reasons rather than simply removing them.

This makes it possible to understand why a transaction was excluded and helps with investigation.

## 6. Repeated Ingestion

I used Snowflake staged-file load tracking to test repeated ingestion.

When the same files were loaded again using the same COPY INTO command, Snowflake skipped the files that had already been processed.

I also tested a separate backfill batch to verify that additional input files could be loaded.

This demonstrates file-level ingestion idempotency; it does not by itself guarantee idempotency for every possible downstream transformation or changed-file scenario.

## 7. Failure Handling

I tested the pipeline using deliberately malformed JSON.

I used `ON_ERROR = 'ABORT_STATEMENT'` so that the invalid input would cause the load statement to fail rather than silently continue.

The failed test file was removed from the stage after the test.

## 8. Performance Testing

I generated a separate dataset containing 10,000 transaction legs.

I loaded it into Snowflake and executed the dbt build to observe the processing time.

The observed results were approximately 1.1 seconds for the Snowflake file load and 7.2 seconds for the dbt build in the tested environment.

## 9. Current Limitations

The current implementation uses synthetic data and has been tested with the datasets described in the project documentation.

Automated scheduling, schema-drift detection, production monitoring and CI/CD integration are areas for future improvement.

## 10. Conclusion

My main design priority was to keep the pipeline understandable, testable and traceable.

The separation of raw, cleaned and final data, together with validation and reconciliation checks, provides a clear way to process transaction records and investigate data quality issues.