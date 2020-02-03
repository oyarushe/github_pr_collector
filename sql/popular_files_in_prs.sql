SELECT f.sha, COUNT(f.sha), MAX(f.filename)
FROM file f
  INNER JOIN association_pull_request_file aprf
    ON f.sha = aprf.file_sha
GROUP BY f.sha
ORDER BY COUNT(f.sha) DESC
LIMIT 3
;
