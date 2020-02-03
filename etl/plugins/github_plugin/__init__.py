"""GitHub Plugin."""

from airflow.plugins_manager import AirflowPlugin

from github_plugin.hooks.github_hook import GitHubHook
from github_plugin.operators.github_pr_cleaner import GitHubPRCleanerOperator
from github_plugin.operators.github_pr_collector import GitHubPRCollectorOperator


class GitHubPlugin(AirflowPlugin):
    """GitHub Plugin."""

    name = "github_plugin"
    hooks = [GitHubHook]
    operators = [GitHubPRCollectorOperator, GitHubPRCleanerOperator]
