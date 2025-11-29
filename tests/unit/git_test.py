from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from standupbrain.git import get_affected_repos, get_git_commits, get_git_commits_local


@pytest.mark.parametrize(
    ('date_str', 'username', 'events_json', 'expected_repos'),
    [
        (
            '2024-01-15',
            'testuser',
            '[{"type":"PushEvent","created_at":"2024-01-15T10:00:00Z","repo":{"name":"org/repo1"}},{"type":"PullRequestEvent","created_at":"2024-01-15T11:00:00Z","repo":{"name":"org/repo2"}}]',
            {'repo1', 'repo2'},
        ),
        (
            '2024-01-15',
            'testuser',
            '[{"type":"PushEvent","created_at":"2024-01-16T10:00:00Z","repo":{"name":"org/repo1"}}]',
            set(),
        ),
        (
            '2024-01-15',
            'testuser',
            '[{"type":"IssueEvent","created_at":"2024-01-15T10:00:00Z","repo":{"name":"org/repo1"}}]',
            set(),
        ),
    ],
)
def test_get_affected_repos(
    date_str: str,
    username: str,
    events_json: str,
    expected_repos: set[str],
) -> None:
    mock_result = Mock()
    mock_result.stdout = events_json

    with patch('subprocess.run', return_value=mock_result):
        result = get_affected_repos(date_str, username)

    assert result == expected_repos


@pytest.mark.parametrize(
    ('affected_repos', 'date_str', 'username', 'git_output', 'expected_count'),
    [
        ({'repo1'}, '2024-01-15', 'testuser', 'abc123|commit msg|body\n', 1),
        ({'repo1', 'repo2'}, '2024-01-15', 'testuser', '', 0),
    ],
)
def test_get_git_commits_local(
    affected_repos: set[str],
    date_str: str,
    username: str,
    git_output: str,
    expected_count: int,
    tmp_path: Path,
) -> None:
    (tmp_path / 'repo1' / '.git').mkdir(parents=True)
    (tmp_path / 'repo2' / '.git').mkdir(parents=True)
    (tmp_path / 'excluded').mkdir()

    mock_result = Mock()
    mock_result.stdout = git_output

    with (
        patch('subprocess.run', return_value=mock_result),
        patch('pathlib.Path.home', return_value=tmp_path.parent),
        patch.object(Path, 'iterdir', return_value=tmp_path.iterdir()),
    ):
        result = get_git_commits_local(affected_repos, date_str, username)

    assert len(result) == expected_count


@pytest.mark.parametrize(
    ('date', 'username', 'email', 'affected_repos', 'commits', 'expected_count'),
    [
        (
            datetime(2024, 1, 15),
            'testuser',
            'test@test.com',
            {'repo1'},
            [{'repo': 'repo1', 'output': 'commit data'}],
            1,
        ),
        (datetime(2024, 1, 15), 'testuser', 'test@test.com', set(), [], 0),
    ],
)
def test_get_git_commits(
    date: datetime,
    username: str,
    email: str,
    affected_repos: set[str],
    commits: list[dict],
    expected_count: int,
) -> None:
    with (
        patch(
            'standupbrain.git.get_affected_repos',
            return_value=affected_repos,
        ) as mock_repos,
        patch(
            'standupbrain.git.get_git_commits_local',
            return_value=commits,
        ) as mock_local,
    ):
        result = get_git_commits(date, username, email)

    mock_repos.assert_called_once_with('2024-01-15', username)
    mock_local.assert_called_once_with(affected_repos, '2024-01-15', email)
    assert len(result) == expected_count
