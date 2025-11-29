import logging
from datetime import datetime

import click

from standupbrain.git import get_git_commits
from standupbrain.git_init import get_local_git_email, get_remote_gh_username, init_git
from standupbrain.jira import make_jira_activity_summary
from standupbrain.jira_init import init_jira
from standupbrain.llm import (
    create_standup_summary_llm_prompt,
    prompt_local_llm,
)
from standupbrain.llm_init import init_llm
from standupbrain.shared import get_previous_workday

logging.basicConfig(level=logging.INFO, format='%(message)s')
logging.getLogger('requests').setLevel(logging.INFO)
log = logging.getLogger(__name__)


@click.group()
@click.version_option()
def main() -> None:
    """CLI for standupbrain, the tool to help you remember what you did yesterday"""


@main.command()
def init() -> None:
    """Initialize standupbrain with your preferred LLM and GitHub/Jira credentials"""
    init_git()
    init_llm()
    init_jira()


@main.command()
@click.option(
    '--author-email',
    '-e',
    help='Git author email for searching local commits',
)
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
    '-u',
    help='GitHub account username for searching remotes in GitHub',
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    default=False,
    help='High verbosity for debugging',
)
def recall(
    author_email: str | None,
    date: datetime | None,
    dry_run: bool,
    github_username: str,
    verbose: bool,
) -> None:
    """Generate a summary of what you did yesterday via GitHub/Jira -> LLM"""
    if verbose or dry_run:
        logging.getLogger().setLevel(logging.DEBUG)

    if not date:
        log.debug('No date provided, using previous workday')
        date = get_previous_workday()
        log.debug('Using date: %s', date)

    if not github_username:
        github_username = get_remote_gh_username()
        click.echo(f'No GitHub username, using local GitHub username {github_username}')

    if not author_email:
        author_email = get_local_git_email()
        click.echo(f'No Git author email, using local Git author email {author_email}')

    commits = get_git_commits(date, github_username, author_email)

    jira_summary = make_jira_activity_summary(date)
    if not commits and not jira_summary:
        click.echo(f'No commits or Jira found for {date}')
        return

    prompt = create_standup_summary_llm_prompt(jira_summary, commits)
    if dry_run:
        log.debug('Prompt size in chars: %s', len(prompt))
        click.echo('Exiting early, not prompting LLM')
        return

    summary = prompt_local_llm(prompt)
    click.echo(summary)
