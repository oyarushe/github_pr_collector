"""
Airflow GitHub Hook.

Implemented based on github third-party library
"""
import functools
import logging
import math
import time

from airflow.hooks.base_hook import BaseHook
from github import Github
from github.GithubException import RateLimitExceededException


def retry_on_rate_limit(github_client: Github):
    """
    Decorator to handle GitHub Rate Limitation.

    :param github_client: GitHub instance
    """
    def decorator(func):
        """Decorator."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Wrapper."""
            try:
                return func(*args, **kwargs)
            except RateLimitExceededException:
                logging.warning("The rate limit is exceeded")

                sec = math.ceil(github_client.rate_limiting_resettime - time.time())
                logging.warning(f"The processing will resume in {sec} seconds")

                time.sleep(sec)
                return func(*args, **kwargs)

        return wrapper

    return decorator


class GitHubHook(BaseHook):
    """Airflow GitHub Hook."""

    def __init__(self, github_conn_id: str = 'github_default'):
        """
        Initialization.

        :param github_conn_id: GitHub connection ID
        """
        self.conn_id = github_conn_id
        self.github_client = None

    def __getattr__(self, item):
        """
        Override __getattr__ to get GitHub methods.

        :param item: method or property
        """
        if hasattr(Github, item):
            if self.github_client is None:
                conn = self.get_connection(self.conn_id)
                self.github_client = Github(conn.login, conn.password)

            return retry_on_rate_limit(self.github_client)(getattr(self.github_client, item))

        return object.__getattribute__(self, item)
