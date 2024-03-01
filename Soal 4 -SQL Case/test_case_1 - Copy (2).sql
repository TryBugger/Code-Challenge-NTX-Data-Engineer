WITH ProductMetrics AS (
    SELECT
        v2ProductName,
        SUM(productRevenue) AS totalRevenue,
        SUM(CAST(productQuantity AS bigint)) AS totalQuantitySold,
        SUM(CAST(productRefundAmount AS bigint)) AS totalRefundAmount
    FROM
        test_table
    WHERE
        productRevenue IS NOT NULL
        AND productQuantity IS NOT NULL
        AND productRefundAmount IS NOT NULL
    GROUP BY
        v2ProductName
)

SELECT
    pm.v2ProductName,
    pm.totalRevenue,
    pm.totalQuantitySold,
    pm.totalRefundAmount,
    pm.totalRevenue - pm.totalRefundAmount AS netRevenue,
    CASE
        WHEN pm.totalRefundAmount > 0.1 * pm.totalRevenue THEN 'High Refund'
        ELSE 'Normal'
    END AS refundFlag
FROM
    ProductMetrics pm
ORDER BY
    netRevenue DESC;
