
{{ config(materialized='table') }}

WITH raw_metrics AS (

    SELECT
        COUNT(*) AS raw_document_count,
        COALESCE(SUM(ARRAY_SIZE(raw_record)), 0) AS raw_leg_count
    FROM {{ source('bank_transactions', 'raw_transactions') }}

),

silver_metrics AS (

    SELECT
        COUNT(*) AS silver_record_count,
        COUNT_IF(is_duplicate = TRUE) AS duplicate_record_count,
        COUNT_IF(is_duplicate = FALSE) AS non_duplicate_record_count
    FROM {{ ref('stg_transaction_legs') }}

),

gold_metrics AS (

    SELECT
        COUNT(*) AS accepted_leg_count,
        COUNT(DISTINCT transaction_id) AS accepted_transaction_count
    FROM {{ ref('fact_valid_transactions') }}

),

rejected_metrics AS (

    SELECT
        COUNT(*) AS rejected_record_count
    FROM {{ ref('rejected_transaction_legs') }}

),

audit_counts AS (

    SELECT
        r.raw_document_count,
        r.raw_leg_count,
        s.silver_record_count,
        s.duplicate_record_count,
        s.non_duplicate_record_count,
        g.accepted_leg_count,
        g.accepted_transaction_count,
        x.rejected_record_count,

        s.silver_record_count - g.accepted_leg_count
            AS records_not_published,

        s.silver_record_count
            - g.accepted_leg_count
            - x.rejected_record_count
            - s.duplicate_record_count
            AS unaccounted_record_count

    FROM raw_metrics r
    CROSS JOIN silver_metrics s
    CROSS JOIN gold_metrics g
    CROSS JOIN rejected_metrics x

)

SELECT
    CURRENT_TIMESTAMP() AS audit_timestamp,

    raw_document_count,
    raw_leg_count,
    silver_record_count,
    duplicate_record_count,
    non_duplicate_record_count,
    accepted_leg_count,
    accepted_transaction_count,
    rejected_record_count,
    records_not_published,
    unaccounted_record_count,

    IFF(
        raw_leg_count = silver_record_count,
        'RECONCILED',
        'COUNT_MISMATCH'
    ) AS ingestion_status,

    IFF(
        accepted_leg_count
        + rejected_record_count
        + duplicate_record_count
        = silver_record_count
        AND unaccounted_record_count = 0,
        'RECONCILED',
        'COUNT_MISMATCH'
    ) AS publication_status

FROM audit_counts
