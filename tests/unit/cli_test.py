from collections.abc import Generator
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from standupbrain.cli import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_dependencies() -> Generator:
    with (
        patch('standupbrain.cli.get_git_commits') as mock_commits,
        patch('standupbrain.cli.make_jira_activity_summary') as mock_jira,
        patch('standupbrain.cli.prompt_local_llm') as mock_llm,
        patch('standupbrain.cli.get_remote_gh_username') as mock_username,
        patch('standupbrain.cli.get_local_git_email') as mock_email,
        patch('standupbrain.cli.get_previous_workday') as mock_prev_day,
        patch('standupbrain.cli.ensure_gh_authenticated') as mock_auth,
    ):
        mock_username.return_value = Mock(stdout='test-user\n')
        mock_email.return_value = Mock(stdout='test-email@test.com\n')
        mock_auth.return_value = True
        mock_prev_day.return_value = datetime(2024, 1, 15)
        yield {
            'commits': mock_commits,
            'jira': mock_jira,
            'llm': mock_llm,
            'username': mock_username,
            'email': mock_email,
            'prev_day': mock_prev_day,
            'mock_auth': mock_auth,
        }


@pytest.mark.parametrize(
    ('date_arg', 'expected_date_used'),
    [
        ('2024-01-15', datetime(2024, 1, 15)),
        (None, None),
    ],
)
def test_recall_with_date(
    runner: CliRunner,
    mock_dependencies: dict,
    date_arg: str | None,
    expected_date_used: datetime | None,
) -> None:
    mock_dependencies['commits'].return_value = [
        {'repo': 'test-repo', 'output': 'commit message here'},
    ]
    mock_dependencies['jira'].return_value = 'jira summary'
    mock_dependencies['llm'].return_value = 'standup output'

    args = ['recall']
    if date_arg:
        args.extend(['--date', date_arg])

    result = runner.invoke(main, args, catch_exceptions=False)

    assert result.exit_code == 0
    assert 'standup output' in result.output
    if expected_date_used:
        mock_dependencies['commits'].assert_called_once()
        actual_date = mock_dependencies['commits'].call_args[0][0]
        assert actual_date == expected_date_used


def test_recall_dry_run(runner: CliRunner, mock_dependencies: dict) -> None:
    mock_dependencies['commits'].return_value = [
        {'repo': 'test-repo', 'output': 'commit message here'},
    ]
    mock_dependencies['jira'].return_value = 'jira summary'

    result = runner.invoke(main, ['recall', '--dry-run'])

    assert result.exit_code == 0
    assert 'not prompting LLM' in result.output
    mock_dependencies['llm'].assert_not_called()


def test_recall_no_data(runner: CliRunner, mock_dependencies: dict) -> None:
    mock_dependencies['commits'].return_value = []
    mock_dependencies['jira'].return_value = ''

    result = runner.invoke(main, ['recall'])

    assert result.exit_code == 0
    assert 'No commits or Jira' in result.output
