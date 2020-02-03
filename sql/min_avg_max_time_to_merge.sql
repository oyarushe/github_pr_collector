SELECT
  MIN(closed_at - created_at),
  AVG(closed_at - created_at),
  MAX(closed_at - created_at)
FROM pull_request
WHERE merged = TRUE
;
