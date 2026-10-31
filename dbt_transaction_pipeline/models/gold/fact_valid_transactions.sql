
{{ config(materialized='table') }}

WITH valid_legs AS (

    SELECT
        transaction_id,
        leg_id,
        account_id,
        counterparty_account_id,
        leg_type,
        amount,
        currency,
        event_timestamp,
        event_sequence,
        reference_id

    FROM {{ ref('stg_transaction_legs') }}

    WHERE
        is_duplicate = FALSE
        AND transaction_id IS NOT NULL
        AND leg_id IS NOT NULL
        AND account_id IS NOT NULL
        AND counterparty_account_id IS NOT NULL
        AND leg_type IN ('DEBIT', 'CREDIT')
        AND amount > 0
        AND currency IS NOT NULL
        AND event_timestamp IS NOT NULL
        AND event_sequence IS NOT NULL
        AND reference_id IS NOT NULL

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

    FROM valid_legs

    GROUP BY transaction_id

),

balanced_transactions AS (

    SELECT transaction_id

    FROM transaction_checks

    WHERE
        leg_count = 2
        AND debit_count = 1
        AND credit_count = 1
        AND debit_amount = credit_amount
        AND currency_count = 1

)

SELECT
    l.*
FROM valid_legs AS l

INNER JOIN balanced_transactions AS b
    ON l.transaction_id = b.transaction_id
