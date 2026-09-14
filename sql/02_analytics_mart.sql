-- Downstream transformation: Staging -> Analytics Mart
INSERT INTO analytics.fact_posts (
    post_id,
    user_id,
    title_length,
    body_word_count,
    created_at
)
SELECT 
    post_id,
    user_id,
    LENGTH(title) AS title_length,
    ARRAY_LENGTH(REGEXP_SPLIT_TO_ARRAY(TRIM(body), '\s+'), 1) AS body_word_count,
    ingested_at AS created_at
FROM staging.stg_posts
ON CONFLICT (post_id) DO UPDATE SET
    title_length = EXCLUDED.title_length,
    body_word_count = EXCLUDED.body_word_count;
