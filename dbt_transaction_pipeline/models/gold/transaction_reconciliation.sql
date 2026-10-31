
{{ config(materialized='table') }}

WITH transaction_summary AS (

    SELECT
        transaction_id,
        COUNT(*) AS leg_count,
        COUNT_IF(leg_type = 'DEBIT') AS debit_count,
        COUNT_IF(leg_type = 'CREDIT') AS credit_count,
        SUM(IFF(leg_type = 'DEBIT', amount, 0)) AS debit_amount,
        SUM(IFF(leg_type = 'CREDIT', amount, 0)) AS credit_amount,
        COUNT(DISTINCT currency) AS currency_count,
        MIN(event_timestamp) AS first_event_timestamp,
        MAX(event_timestamp) AS last_event_timestamp

    FROM {{ ref('stg_transaction_legs') }}

    WHERE is_duplicate = FALSE
      AND transaction_id IS NOT NULL

    GROUP BY transaction_id

)

SELECT
    transaction_id,
    leg_count,
    debit_count,
    credit_count,
    debit_amount,
    credit_amount,
    currency_count,
    first_event_timestamp,
    last_event_timestamp,

    IFF(
        leg_count = 2
        AND debit_count = 1
        AND credit_count = 1
        AND debit_amount = credit_amount
        AND currency_count = 1,
        TRUE,
        FALSE
    ) AS is_balanced,

    IFF(currency_count = 1, TRUE, FALSE) AS has_consistent_currency

FROM transaction_summary
