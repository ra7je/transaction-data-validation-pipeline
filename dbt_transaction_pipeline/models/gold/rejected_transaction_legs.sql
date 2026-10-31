
{{ config(materialized='table') }}

WITH source_legs AS (

    SELECT *
    FROM {{ ref('stg_transaction_legs') }}

),

transaction_checks AS (

    SELECT
        transaction_id,
        COUNT(*) AS leg_count,
        COUNT_IF(leg_type = 'DEBIT') AS debit_count,
        COUNT_IF(leg_type = 'CREDIT') AS credit_count,
        SUM(IFF(leg_type = 'DEBIT', amount, 0)) AS debit_amount,
        SUM(IFF(leg_type = 'CREDIT', amount, 0)) AS credit_amount,
        COUNT(DISTINCT currency) AS currency_count

    FROM source_legs
    WHERE COALESCE(is_duplicate, FALSE) = FALSE
      AND transaction_id IS NOT NULL
    GROUP BY transaction_id

),

classified AS (

    SELECT
        s.*,

        CASE
            WHEN COALESCE(s.is_duplicate, FALSE) = TRUE
                THEN 'DUPLICATE_LEG'
            WHEN s.transaction_id IS NULL
                THEN 'MISSING_TRANSACTION_ID'
            WHEN s.leg_id IS NULL
                THEN 'MISSING_LEG_ID'
            WHEN s.account_id IS NULL
                THEN 'MISSING_ACCOUNT_ID'
            WHEN s.counterparty_account_id IS NULL
                THEN 'MISSING_COUNTERPARTY_ACCOUNT'
            WHEN s.leg_type NOT IN ('DEBIT', 'CREDIT')
                 OR s.leg_type IS NULL
                THEN 'INVALID_LEG_TYPE'
            WHEN s.amount IS NULL OR s.amount <= 0
                THEN 'INVALID_AMOUNT'
            WHEN s.currency IS NULL
                THEN 'MISSING_CURRENCY'
            WHEN s.event_timestamp IS NULL
                THEN 'MISSING_EVENT_TIMESTAMP'
            WHEN s.event_sequence IS NULL
                THEN 'MISSING_EVENT_SEQUENCE'
            WHEN s.reference_id IS NULL
                THEN 'MISSING_REFERENCE_ID'
            WHEN t.transaction_id IS NULL
                THEN 'MISSING_TRANSACTION_SUMMARY'
            WHEN t.leg_count != 2
                THEN 'INVALID_LEG_COUNT'
            WHEN t.debit_count != 1 OR t.credit_count != 1
                THEN 'INVALID_DEBIT_CREDIT_PAIR'
            WHEN t.debit_amount != t.credit_amount
                THEN 'UNBALANCED_TRANSACTION'
            WHEN t.currency_count != 1
                THEN 'CURRENCY_MISMATCH'
            ELSE NULL
        END AS rejection_reason

    FROM source_legs s

    LEFT JOIN transaction_checks t
        ON s.transaction_id = t.transaction_id

)

SELECT *
FROM classified
WHERE rejection_reason IS NOT NULL
