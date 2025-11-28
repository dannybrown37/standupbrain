import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

log = logging.getLogger(__name__)


def get_git_commits(date: datetime, github_username: str) -> list[dict]:
    date_str = date.strftime('%Y-%m-%d')
    log.debug('Getting commits for %s', date_str)
    affected_repos = get_affected_repos(date_str, github_username)
    log.debug('Affected repos: %s', affected_repos)
    return get_git_commits_local(affected_repos, date_str, github_username)


def get_affected_repos(date_str: str, github_username: str) -> set[str]:
    events_result = subprocess.run(
        ['gh', 'api', f'/users/{github_username}/events', '--paginate'],
        capture_output=True,
        text=True,
        check=True,
    )

    affected_repos = set()
    decoder = json.JSONDecoder()
    raw = events_result.stdout.strip()
    idx = 0

    while idx < len(raw):
        try:
            events, end_idx = decoder.raw_decode(raw, idx)
            for event in events:
                if (
                    event['type'] == 'PushEvent'
                    and event['created_at'][:10] == date_str
                ):
                    repo_name = event['repo']['name'].split('/')[-1]
                    affected_repos.add(repo_name)
            idx = end_idx
        except json.JSONDecodeError:
            break

    return affected_repos


def get_git_commits_local(
    affected_repos: set[str],
    date_str: str,
    github_username: str,
) -> list[dict]:
    projects_dir = Path.home() / 'projects'
    all_commits = []

    for repo in projects_dir.iterdir():
        if not (repo / '.git').exists() or repo.name not in affected_repos:
            continue

        result = subprocess.run(
            [
                'git',
                '-C',
                str(repo),
                'log',
                '--all',
                f'--since={date_str} 00:00',
                f'--until={date_str} 23:59',
                f'--author={github_username}',
                '--format=%H|%s|%b',
                '--patch',
            ],
            capture_output=True,
            text=True,
        )

        if result.stdout:
            all_commits.append({'repo': repo.name, 'output': result.stdout})

    log.debug('Found %d commits', len(all_commits))
    return all_commits
