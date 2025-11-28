import logging
from pprint import pformat
from datetime import datetime

import click

from standupbrain.git import get_git_commits
from standupbrain.llm_init import init_llm
from standupbrain.llm_prompt import (
    format_prompt_for_llm,
    generate_standup_summary,
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
        log.setLevel(verbosity.upper())


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
def generate(
    date: datetime | None,
    github_username: str,
) -> None:
    if not date:
        log.debug('No date provided, using previous workday')
        date = get_previous_workday()
        log.debug('Using date: %s', date)
    commits = get_git_commits(date, github_username)
    log.debug(pformat(commits))
    log.debug('Found %d commits', len(commits))
    if not commits:
        click.echo('No commits found for that date')
        return

    prompt = format_prompt_for_llm(commits)
    summary = generate_standup_summary(prompt)
    click.echo(summary)
