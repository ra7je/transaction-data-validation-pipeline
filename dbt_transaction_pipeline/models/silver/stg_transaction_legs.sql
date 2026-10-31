{{ config(materialized='table') }}

WITH source_data AS (

    SELECT
        f.value AS transaction_data
    FROM {{ source('bank_transactions', 'raw_transactions') }} AS r,
         LATERAL FLATTEN(INPUT => r.raw_record) AS f

),

cleaned AS (

    SELECT
        NULLIF(TRIM(transaction_data:transaction_id::VARCHAR), '') AS transaction_id,
        NULLIF(TRIM(transaction_data:leg_id::VARCHAR), '') AS leg_id,
        NULLIF(TRIM(transaction_data:account_id::VARCHAR), '') AS account_id,
        NULLIF(TRIM(transaction_data:counterparty_account_id::VARCHAR), '') AS counterparty_account_id,
        UPPER(TRIM(transaction_data:leg_type::VARCHAR)) AS leg_type,
        TRY_TO_DECIMAL(transaction_data:amount::VARCHAR, 18, 2) AS amount,
        UPPER(TRIM(transaction_data:currency::VARCHAR)) AS currency,
        TRY_TO_TIMESTAMP_TZ(transaction_data:event_timestamp::VARCHAR) AS event_timestamp,
        TRY_TO_NUMBER(transaction_data:event_sequence::VARCHAR) AS event_sequence,
        NULLIF(TRIM(transaction_data:reference_id::VARCHAR), '') AS reference_id
    FROM source_data

),

ranked AS (

    SELECT
        *,
        CASE
            WHEN leg_id IS NOT NULL THEN
                ROW_NUMBER() OVER (
                    PARTITION BY leg_id
                    ORDER BY event_timestamp, event_sequence, transaction_id
                )
            ELSE 1
        END AS duplicate_rank
    FROM cleaned

)

SELECT
    *,
    IFF(leg_id IS NOT NULL AND duplicate_rank > 1, TRUE, FALSE)
        AS is_duplicate
FROM ranked