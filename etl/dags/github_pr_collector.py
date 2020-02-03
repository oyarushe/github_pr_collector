"""
Airflow DAG to collect Pull Requests from GitHub.

Configuration via Airflow Variables:
{
  "github_pr_collector": {
    "load_type": "incremental",         # Load type. Allowed: incremental, full
    "repos": "apache/airflow"           # The list of repositories. Comma separated
  }
}
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.github_plugin import GitHubPRCleanerOperator, GitHubPRCollectorOperator

with DAG(
    dag_id="collect_github_pr",
    catchup=False,
    max_active_runs=1,
    schedule_interval=timedelta(days=1),
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'start_date': datetime(2019, 1, 1),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 0,
        'retry_delay': timedelta(minutes=5)
    }
) as dag:
    delete_deprecated_pr = GitHubPRCleanerOperator(
        task_id='delete_deprecated_pr',
        postgres_conn_id='postgres',
        load_type='{{ var.json.github_pr_collector.load_type }}',
        repos='{{ var.json.github_pr_collector.repos }}'
    )

    load_github_pr = GitHubPRCollectorOperator(
        task_id='load_github_pr',
        github_conn_id='github',
        postgres_conn_id='postgres',
        load_type='{{ var.json.github_pr_collector.load_type }}',
        repos='{{ var.json.github_pr_collector.repos }}'
    )

    delete_deprecated_pr >> load_github_pr
