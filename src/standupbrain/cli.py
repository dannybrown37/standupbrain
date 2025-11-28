from datetime import datetime
from pprint import pprint
import click

from standupbrain.git import get_git_commits
from standupbrain.llm import init_llm
from standupbrain.utils import get_previous_workday


@click.group()
def main() -> None:
    pass


@main.command()
def init() -> None:
    init_llm()


@main.command()
@click.option(
    '--date',
    '-d',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='Specific date to generate update for (YYYY-MM-DD)',
)
@click.option(
    '--github-username',
    '-g',
    '-u',
    help='GitHub username for the search',
)
def generate(date: datetime | None, github_username: str) -> None:
    if not date:
        date = get_previous_workday()
    commits = get_git_commits(date, github_username)
    pprint(commits)
