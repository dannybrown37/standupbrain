import json
from datetime import datetime
import subprocess


def get_git_commits(date: datetime, github_username: str) -> list[dict]:
    date_str = date.strftime('%Y-%m-%d')

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
                    affected_repos.add(event['repo']['name'])
            idx = end_idx
        except json.JSONDecodeError:
            break

    all_commits = []
    for repo in affected_repos:
        commits_result = subprocess.run(
            ['gh', 'api', f'/repos/{repo}/commits', '-f', 'per_page=100'],
            capture_output=True,
            text=True,
        )

        if commits_result.returncode == 0 and commits_result.stdout.strip():
            commits = json.loads(commits_result.stdout)
            for commit in commits:
                commit_date = commit['commit']['author']['date'][:10]
                commit_author = commit['commit']['author']['name']
                if (
                    commit_date == date_str
                    and commit_author == github_username
                ):
                    all_commits.append(commit)

    return all_commits
