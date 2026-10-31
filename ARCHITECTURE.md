# Project Architecture

## 1. Overview

I designed this pipeline to process bank transaction data from the time it is generated until the final validated records are available.

The pipeline uses Python, Snowflake and dbt. I separated the processing into different layers so that raw data, cleaned data and final results can be managed independently.

## 2. Architecture Flow

The data moves through the following stages:

**Python → Snowflake Stage → Bronze → Silver → Gold → Audit**

### Python – Data Generation

I use Python to generate synthetic bank transaction records in JSON format.

Each transaction contains debit and credit entries, account details, amount, currency, timestamp, event sequence and reference ID.

The generator uses a fixed random seed so that I can reproduce the same sample data when needed.

### Snowflake Stage – Data Ingestion

The generated JSON files are uploaded to a Snowflake internal stage.

I use the `COPY INTO` command to load the files into the raw Bronze table.

### Bronze – Raw Data Storage

The Bronze layer stores the original JSON data in Snowflake VARIANT format.

I also maintain the source filename and ingestion timestamp to help identify where the data came from and when it was loaded.

### Silver – Data Transformation

The Silver layer extracts individual transaction legs using `LATERAL FLATTEN`.

I standardize the fields, convert values into the required data types and identify duplicate leg IDs.

### Gold – Final Data

The Gold layer contains the outputs required for downstream use:

- Valid transaction records
- Rejected records with rejection reasons
- Transaction reconciliation results
- Pipeline audit information

### Audit – Pipeline Monitoring

The audit model compares record counts across the processing layers.

It helps identify whether records have been accounted for during ingestion and publication.

## 3. Main Components

| Component | Responsibility |
|---|---|
| Python generator | Generates synthetic transaction data |
| Snowflake internal stage | Holds uploaded JSON files |
| Bronze table | Stores original raw data |
| Silver models | Clean and standardize transaction records |
| Gold models | Publish accepted and rejected records |
| Audit model | Tracks record counts and reconciliation |
| Pytest | Tests Python validation logic |
| dbt tests | Checks transformed data |

## 4. Why I Used This Architecture

I kept the raw data separate from the transformed data so that the original input is preserved.

The Silver layer handles cleaning and preparation, while the Gold layer contains the final business results.

This separation also makes it easier to identify where an issue occurred and investigate rejected records.

## 5. Reliability

I tested the pipeline with:

- A separate backfill batch
- Repeated ingestion of previously loaded files
- Malformed JSON input
- Duplicate transaction legs
- Invalid transaction amounts and currencies
- Debit-credit mismatches
- A larger dataset containing 10,000 transaction legs

These tests helped me verify the pipeline's ingestion, validation and reconciliation behaviour.

## 6. Current Scope

The current implementation uses synthetic data and a local Python project connected to Snowflake.

Automated scheduling, production orchestration and automated schema-drift alerts are possible future improvements.