import logging
from datetime import datetime

import click

from standupbrain.git import get_git_commits
from standupbrain.jira import make_jira_activity_summary
from standupbrain.llm_init import init_llm
from standupbrain.llm_prompt import (
    create_standup_summary_llm_prompt,
    prompt_local_llm,
)
from standupbrain.shared import get_previous_workday

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)


@click.group()
@click.option(
    '--verbosity',
    '-v',
    type=click.Choice(['debug', 'info', 'warning', 'error', 'critical']),
    help='Verbosity level',
)
def main(verbosity: str) -> None:
    if verbosity:
        logging.getLogger().setLevel(verbosity.upper())


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
def jira(date: str) -> None:
    summary = make_jira_activity_summary(date)
    click.echo(summary)

@main.command()
@click.option(
    '--date',
    '-d',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='Specific date to generate update for (YYYY-MM-DD)',
)
@click.option(
    '--github-username',
    '--author-email',
    '-g',
    '-u',
    help='GitHub username or email for the search',
)
def generate(
    date: datetime | None,
    github_username: str,
) -> None:
    if not date:
        log.debug('No date provided, using previous workday')
        date = get_previous_workday()
        log.debug('Using date: %s', date)
    commits = get_git_commits(date, github_username)

    jira_summary = make_jira_activity_summary(date)
    if not commits and not jira_summary:
        log.error('No commits or Jira found for %s', date)
        return

    prompt = create_standup_summary_llm_prompt(jira_summary, commits)
    summary = prompt_local_llm(prompt)
    click.echo(summary)
