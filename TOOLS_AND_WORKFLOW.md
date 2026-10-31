# Development Tools and Project Workflow

## 1. Tools and Technologies Used

The transaction data validation pipeline was developed using industry-standard tools and technologies.

| Tool / Technology | Purpose |
|---|---|
| Python | Transaction data generation and validation |
| Snowflake | Cloud data warehousing and data storage |
| SQL | Data transformation, validation and reconciliation |
| dbt | Data modelling and data quality testing |
| Pytest | Unit testing and validation of Python logic |
| Git | Version control and source code management |
| GitHub | Repository management and project documentation |
| VS Code | Development and code management |

## 2. Development Workflow

The project follows a structured data engineering workflow:

1. **Data Generation:** Generated synthetic bank transaction records containing debit and credit entries.
2. **Data Ingestion:** Loaded JSON transaction files into Snowflake using an internal stage and `COPY INTO`.
3. **Bronze Layer:** Stored the incoming raw transaction data.
4. **Silver Layer:** Applied data cleaning, validation and duplicate detection using dbt.
5. **Gold Layer:** Prepared accepted transaction records for downstream analysis.
6. **Reconciliation:** Checked debit and credit consistency and transaction-level reconciliation.
7. **Audit:** Recorded pipeline execution information and validation results.
8. **Testing:** Used Pytest and dbt tests to verify the implementation.
9. **Version Control:** Maintained the source code and documentation in GitHub.

## 3. Testing and Validation

The pipeline was tested using different scenarios, including:

- Valid transaction records.
- Missing and invalid fields.
- Duplicate transaction legs.
- Debit and credit amount mismatches.
- Backfill data ingestion.
- Repeated file ingestion.
- Large-volume transaction data.

## 4. Verification Results

- Python unit tests: 13 passed.
- dbt models: 5 processed.
- dbt tests: 11 passed.
- dbt seeds: 6 processed.
- Total successful dbt operations: 22.

## 5. Project Outcome

The project demonstrates an end-to-end transaction data validation workflow using Python, Snowflake, SQL and dbt. It covers data ingestion, transformation, quality checks, reconciliation, testing and version control.