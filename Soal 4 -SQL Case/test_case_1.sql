WITH CountryRevenue AS (
    SELECT
        country,
        SUM(CAST(totalTransactionRevenue AS DECIMAL)) AS totalRevenue
    FROM
        test_table
    WHERE
        totalTransactionRevenue IS NOT NULL
    GROUP BY
        country
)

SELECT
    tt.channelGrouping,
    cr.country,
    SUM(CAST(tt.totalTransactionRevenue AS DECIMAL)) AS totalRevenue
FROM
    test_table tt
JOIN
    CountryRevenue cr ON tt.country = cr.country
WHERE
    tt.totalTransactionRevenue IS NOT NULL
GROUP BY
    tt.channelGrouping, cr.country
ORDER BY
    totalRevenue DESC
LIMIT 5;