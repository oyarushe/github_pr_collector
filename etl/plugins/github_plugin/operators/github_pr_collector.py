"""
Airflow GitHub PR Collector Operator.

Dedicated to load GitHub Pull Request to Database (PostgreSQL)
Implemented two type of load:
 - incremental: load only for the period that specified in the init method;
 - full: load all data to DB
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from airflow.models import BaseOperator
from github.File import File
from github.PaginatedList import PaginatedList
from github.PullRequest import PullRequest
from sqlalchemy.dialects.postgresql import insert

from github_plugin.hooks.github_hook import GitHubHook


class GitHubPRCollectorOperator(BaseOperator):
    """Airflow GitHub Collector Operator."""

    template_fields = ['load_type', 'repos']

    LOAD_TYPES = ["incremental", "full"]

    def __init__(
        self,
        repos: str,
        github_conn_id: str = 'github_default',
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
        :param github_conn_id: GitHub connection ID
        :param postgres_conn_id: Postgres connection ID
        :param load_type: type of load, allowed: incremental, full
        :param repos_sep: separator for repos
        :param period: period of load for incremental load. Default: 1 day
        """
        from airflow_utils.models.base import DB  # to resolve circular import

        self.github_hook = GitHubHook(github_conn_id)
        self.db = DB(postgres_conn_id)

        self.load_type = load_type
        self.repos = repos
        self.repos_sep = repos_sep

        self.period = period or timedelta(days=1)

        super().__init__(*args, **kwargs)

    def _process_pull_files(self, pull_id: int, files: 'PaginatedList[File]'):
        """
        Load Pull Request files.

        :param pull_id: Pull Request ID
        :param files: the list of pull request's files
        """
        from airflow_utils.models import AssociationPullRequestFile, File  # to resolve circular import
        file_values = []
        association_values = []
        for file in files:
            file_values.append({
                "sha": file.sha,
                "filename": file.filename
            })

            association_values.append({
                "pull_request_id": pull_id,
                "file_sha": file.sha
            })

        files_stmnt = insert(File).values(file_values).on_conflict_do_nothing(index_elements=[
            'sha'
        ])

        association_stmnt = insert(AssociationPullRequestFile) \
            .values(association_values) \
            .on_conflict_do_nothing(index_elements=[
                'pull_request_id',
                'file_sha'
            ])
        self.db.session.execute(files_stmnt)
        self.db.session.execute(association_stmnt)

    def _process_pull_request(self, repo_id: int, pull: PullRequest):
        """
        Load Pull Request data.

        :param repo_id: Repository ID
        :param pull: Pull Request data
        """
        from airflow_utils.models import PullRequest  # to resolve circular import

        pull_request_stmnt = insert(PullRequest).values({
            "id": pull.id,
            "title": pull.title,
            "created_at": pull.created_at,
            "closed_at": pull.closed_at,
            "merged": pull.merged,
            "repo_id": repo_id,
        }).on_conflict_do_nothing(index_elements=['id'])

        self.db.session.execute(pull_request_stmnt)

        logging.info(f"Found {pull.changed_files} files to process for PR {pull.title}")
        if pull.changed_files:
            self._process_pull_files(pull.id, pull.get_files())
            logging.info(f"All files processed for PR {pull.title}")

        self.db.session.commit()

    def _process_repo(self, repo_name: str, execution_date: datetime):
        """
        Load Repository data.

        :param repo_name: full name of repository
        :param execution_date: Airflow Execution Date
        """
        from airflow_utils.models import Repo  # to resolve circular import
        repo = self.github_hook.get_repo(repo_name)

        insert_repo_stmnt = insert(Repo) \
            .values({
                "id": repo.id,
                "name": repo.full_name
            }) \
            .on_conflict_do_nothing(index_elements=['id'])

        self.db.session.execute(insert_repo_stmnt)
        self.db.session.commit()

        pulls = repo.get_pulls(
            state='closed',
            sort='closed',
            direction='desc'
        )

        for pull in pulls:
            if self.load_type == "incremental" and pull.closed_at < execution_date - self.period:
                break
            logging.info(f"Processing pull request {pull.title}")
            self._process_pull_request(repo.id, pull)

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
            self._process_repo(repo, context["execution_date"])
