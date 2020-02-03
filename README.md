##Getting Started

1. `make run` - build Airflow and PostgeSQL Docker images, run containers. Airflow is available on http://127.0.0.1:9090
2. `make init-db` - initialize DB in PostgreSQL
3. Edit connection `github` to set your credentials
4. Edit variables to set repositories and load type

## Load types
- incremental, updates data only for the specific period
- full load, updates the whole data

##SQL
- [Minimum, Average, Maximum time to merge PR](sql/min_avg_max_time_to_merge.sql)
- [Top 3 files in PRs](sql/popular_files_in_prs.sql)
