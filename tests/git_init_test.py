import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from standupbrain.git_init import (
    get_git_credentials,
    init_git,
)


@pytest.fixture
def mock_config_path(tmp_path: Path) -> Generator:
    config_path = tmp_path / 'config.json'
    with patch('standupbrain.git_init.get_config_path', return_value=config_path):
        yield config_path


@pytest.mark.parametrize(
    ('existing_config', 'expected'),
    [
        ({}, None),
        (
            {'git_email': 'test@example.com', 'gh_username': 'testuser'},
            ('test@example.com', 'testuser'),
        ),
        ({'git_email': 'test@example.com'}, None),
        ({'gh_username': 'testuser'}, None),
        (
            {
                'root_url': 'https://jira.com',
                'git_email': 'test@example.com',
                'gh_username': 'testuser',
            },
            ('test@example.com', 'testuser'),
        ),
    ],
)
def test_get_git_credentials(
    mock_config_path: Path,
    existing_config: dict,
    expected: tuple[str, str] | None,
) -> None:
    if existing_config:
        mock_config_path.write_text(json.dumps(existing_config))

    result = get_git_credentials()
    assert result == expected


@patch('standupbrain.git_init.click.echo')
@patch('standupbrain.git_init.click.prompt')
@patch('standupbrain.git_init.click.confirm')
@patch('standupbrain.git_init.get_local_git_email')
@patch('standupbrain.git_init.get_remote_gh_username')
def test_init_git_new_config(
    mock_gh_username: Mock,
    mock_git_email: Mock,
    mock_confirm: Mock,
    mock_prompt: Mock,
    mock_echo: Mock,
    mock_config_path: Path,
) -> None:
    mock_git_email.return_value = 'local@example.com'
    mock_gh_username.return_value = 'local-user'
    mock_prompt.side_effect = ['user@example.com', 'gh-user']
    mock_confirm.return_value = True

    init_git()

    config = json.loads(mock_config_path.read_text())
    assert config['git_email'] == 'user@example.com'
    assert config['gh_username'] == 'gh-user'


@patch('standupbrain.git_init.click.echo')
@patch('standupbrain.git_init.click.prompt')
@patch('standupbrain.git_init.click.confirm')
def test_init_git_existing_keep(
    mock_confirm: Mock,
    mock_prompt: Mock,
    mock_echo: Mock,
    mock_config_path: Path,
) -> None:
    mock_config_path.write_text(
        json.dumps(
            {'git_email': 'existing@example.com', 'gh_username': 'existing-user'},
        ),
    )
    mock_confirm.return_value = False

    init_git()

    config = json.loads(mock_config_path.read_text())
    assert config['git_email'] == 'existing@example.com'
    assert config['gh_username'] == 'existing-user'


@patch('standupbrain.git_init.click.echo')
@patch('standupbrain.git_init.click.prompt')
@patch('standupbrain.git_init.click.confirm')
def test_init_git_existing_overwrite(
    mock_confirm: Mock,
    mock_prompt: Mock,
    mock_echo: Mock,
    mock_config_path: Path,
) -> None:
    mock_config_path.write_text(
        json.dumps({'git_email': 'old@example.com', 'gh_username': 'olduser'}),
    )
    mock_confirm.side_effect = [True, True]
    mock_prompt.side_effect = ['new@example.com', 'newuser']

    init_git()

    config = json.loads(mock_config_path.read_text())
    assert config['git_email'] == 'new@example.com'
    assert config['gh_username'] == 'newuser'


@patch('standupbrain.git_init.click.echo')
@patch('standupbrain.git_init.click.prompt')
@patch('standupbrain.git_init.click.confirm')
@patch('standupbrain.git_init.get_local_git_email')
@patch('standupbrain.git_init.get_remote_gh_username')
def test_init_git_preserves_other_config(
    mock_gh_username: Mock,
    mock_git_email: Mock,
    mock_confirm: Mock,
    mock_prompt: Mock,
    mock_echo: Mock,
    mock_config_path: Path,
) -> None:
    mock_config_path.write_text(
        json.dumps({'root_url': 'https://jira.com', 'api_token': 'secret'}),
    )
    mock_git_email.return_value = None
    mock_gh_username.return_value = None
    mock_prompt.side_effect = ['user@example.com', 'gh-user']
    mock_confirm.return_value = True

    init_git()

    config = json.loads(mock_config_path.read_text())
    assert config['root_url'] == 'https://jira.com'
    assert config['api_token'] == 'secret'
    assert config['git_email'] == 'user@example.com'
    assert config['gh_username'] == 'gh-user'
