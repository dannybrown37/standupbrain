import logging
from datetime import datetime
import subprocess

import click

from standupbrain.git import get_git_commits
from standupbrain.jira import make_jira_activity_summary
from standupbrain.jira_init import init_jira
from standupbrain.llm_init import init_llm
from standupbrain.llm import (
    create_standup_summary_llm_prompt,
    prompt_local_llm,
)
from standupbrain.shared import get_previous_workday

logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger('requests').setLevel(logging.INFO)
log = logging.getLogger(__name__)


@click.group()
def main() -> None: ...


@main.command()
def init() -> None:
    init_llm()
    init_jira()


# region Temp
@main.command()
@click.option(
    '--date',
    '-d',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='Specific date to generate update for (YYYY-MM-DD)',
)
def jira(date: str) -> None:
    logging.getLogger().setLevel(logging.DEBUG)
    summary = make_jira_activity_summary(date)
    click.echo(summary)


# endregion


@main.command()
@click.option(
    '--date',
    '-d',
    type=click.DateTime(formats=['%Y-%m-%d']),
    help='Specific date to generate update for (YYYY-MM-DD)',
)
@click.option(
    '--dry-run',
    '--dry_run',
    is_flag=True,
    default=False,
    help='Do not actually prompt the LLM, just query the APIs and print the prompt',
)
@click.option(
    '--github-username',
    '--author-email',
    '-g',
    '-u',
    help='GitHub username or email for the search',
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='High verbosity for debugging',
)
def generate(
    date: datetime | None,
    dry_run: bool,
    github_username: str,
    verbose: bool,
) -> None:
    if verbose or dry_run:
        logging.getLogger().setLevel(logging.DEBUG)

    if not date:
        log.debug('No date provided, using previous workday')
        date = get_previous_workday()
        log.debug('Using date: %s', date)

    if not github_username:
        result = subprocess.run(
            ['gh', 'api', 'user', '--jq', '.login'],
            capture_output=True,
            text=True,
            check=True,
        )
        github_username = result.stdout.strip()
        log.debug('No GitHub username, using local GitHub username %s', github_username)

    commits = get_git_commits(date, github_username)

    jira_summary = make_jira_activity_summary(date)
    if not commits and not jira_summary:
        log.error('No commits or Jira found for %s', date)
        return

    prompt = create_standup_summary_llm_prompt(jira_summary, commits)
    if dry_run:
        log.debug('Prompt size in chars: %s', len(prompt))
        click.echo('Exiting early, not prompting LLM')
        return

    summary = prompt_local_llm(prompt)
    click.echo(summary)
