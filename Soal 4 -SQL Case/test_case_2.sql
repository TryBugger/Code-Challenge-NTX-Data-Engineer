WITH UserMetrics AS (
    SELECT
        fullVisitorId,
        AVG(timeOnSite) AS avgTimeOnSite,
        AVG(pageviews) AS avgPageviews,
        AVG(sessionQualityDim) AS avgSessionQualityDim
    FROM
        test_table
    WHERE
        timeOnSite IS NOT NULL
        AND pageviews IS NOT NULL
        AND sessionQualityDim IS NOT NULL
    GROUP BY
        fullVisitorId
)

SELECT
    um.fullVisitorId,
    um.avgTimeOnSite,
    um.avgPageviews,
    um.avgSessionQualityDim
FROM
    UserMetrics um
WHERE
    um.avgTimeOnSite > (SELECT AVG(timeOnSite) FROM test_table WHERE timeOnSite IS NOT NULL)
    AND um.avgPageviews < (SELECT AVG(pageviews) FROM test_table WHERE pageviews IS NOT NULL)
ORDER BY
    um.avgTimeOnSite DESC;