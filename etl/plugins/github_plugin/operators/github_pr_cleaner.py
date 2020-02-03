"""
Airflow GitHub PR Cleaner Operator.

Dedicated to delete deprecated data or data that will be reloaded
Implemented two type of load:
 - incremental: delete only for the period that specified in the init method;
 - full: delete the whole data
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from airflow.models import BaseOperator
from sqlalchemy.sql.expression import delete, select


class GitHubPRCleanerOperator(BaseOperator):
    """Airflow GitHub PR Cleaner Operator."""

    template_fields = ['load_type', 'repos']

    LOAD_TYPES = ["incremental", "full"]

    def __init__(
        self,
        repos: str,
        postgres_conn_id: str = 'postgres_default',
        load_type: str = 'incremental',
        repos_sep: str = ',',
        period: Optional[str] = None,  # only for incremental load, default 1 day
        *args,
        **kwargs
    ):
        """
        Initialization.

        :param repos: comma separated list of repos
        :param postgres_conn_id: Postgres connection ID
        :param load_type: type of load, allowed: incremental, full
        :param repos_sep: separator for repos
        :param period: period of load for incremental load. Default: 1 day
        """
        from airflow_utils.models.base import DB  # to resolve circular import

        self.db = DB(postgres_conn_id)

        self.load_type = load_type
        self.repos = repos
        self.repos_sep = repos_sep

        self.period = period or timedelta(days=1)

        super().__init__(*args, **kwargs)

    def _delete_period(self, repo_name: str, execution_date: datetime):
        """
        Delete data for specified period.

        :param repo_name: full name of repository
        :param execution_date: Airflow Execution Date
        """
        from airflow_utils.models import PullRequest, Repo  # to resolve circular import

        delete_stmnt = delete(PullRequest).where(
            PullRequest.repo_id == select([Repo.id]).where(
                Repo.name == repo_name
            )
        ).where(
            PullRequest.closed_at >= (execution_date - self.period).date()
        )

        logging.info(str(delete_stmnt))
        self.db.session.execute(delete_stmnt)
        self.db.session.commit()

    def _full_delete(self, repo_name: str):
        """
        Delete the whole data.

        :param repo_name: full name of repository
        """
        from airflow_utils.models import PullRequest, Repo  # to resolve circular import

        delete_stmnt = delete(PullRequest).where(
            PullRequest.repo_id == select([Repo.id]).where(
                Repo.name == repo_name
            )
        )

        logging.info(str(delete_stmnt))

        self.db.session.execute(delete_stmnt)
        self.db.session.commit()

    def execute(self, context):
        """
        Operator Execution.

        :param context: Airflow execution context
        """
        if self.load_type not in self.LOAD_TYPES:
            raise ValueError(f"Load type {self.load_type} is not allowed")

        if isinstance(self.repos, str):
            self.repos = self.repos.split(self.repos_sep)

        if not isinstance(self.repos, list):
            raise ValueError(f"GitHub repositories value {self.repos} should be list")

        for repo in self.repos:
            logging.info(f"Processing repository {repo}")
            if self.load_type == "full":
                logging.info("Executing full delete...")
                self._full_delete(repo)
            else:
                logging.info(f"Execution delete for the period {self.period}...")
                self._delete_period(repo, context["execution_date"])
