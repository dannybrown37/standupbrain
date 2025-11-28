import json
from pathlib import Path
from unittest.mock import patch

import pytest

from standupbrain.jira_init import get_jira_credentials, init_jira


@pytest.mark.parametrize(
    ('existing_creds', 'prompts', 'confirm_responses', 'expected_saved'),
    [
        (
            None,
            ['https://company.atlassian.net', 'user@example.com', 'token123'],
            [True],
            {
                'root_url': 'https://company.atlassian.net',
                'email': 'user@example.com',
                'api_token': 'token123',
            },
        ),
        (
            ('https://old.atlassian.net', 'old@example.com', 'old-token'),
            ['https://new.atlassian.net', 'new@example.com', 'new-token'],
            [True, True],
            {
                'root_url': 'https://new.atlassian.net',
                'email': 'new@example.com',
                'api_token': 'new-token',
            },
        ),
        (
            ('https://old.atlassian.net', 'old@example.com', 'old-token'),
            [],
            [False],
            None,
        ),
    ],
)
def test_init_jira(
    tmp_path: Path,
    existing_creds: tuple[str, str, str] | None,
    prompts: list[str],
    confirm_responses: list[bool],
    expected_saved: dict | None,
) -> None:
    config_file = tmp_path / 'credentials.json'

    if existing_creds:
        config_file.write_text(
            json.dumps(
                {
                    'root_url': existing_creds[0],
                    'email': existing_creds[1],
                    'api_token': existing_creds[2],
                },
            ),
        )

    with (
        patch('standupbrain.jira_init.get_config_path', return_value=config_file),
        patch('click.echo'),
        patch('click.prompt', side_effect=prompts),
        patch('click.confirm', side_effect=confirm_responses),
    ):
        init_jira()

    if expected_saved:
        assert config_file.exists()
        data = json.loads(config_file.read_text())
        assert data == expected_saved
    elif existing_creds:
        data = json.loads(config_file.read_text())
        assert data['email'] == existing_creds[1]


def test_get_jira_credentials_exists(tmp_path: Path) -> None:
    config_file = tmp_path / 'credentials.json'
    config_file.write_text(
        json.dumps(
            {
                'root_url': 'https://test.atlassian.net',
                'email': 'test@example.com',
                'api_token': 'test-token',
            },
        ),
    )

    with patch('standupbrain.jira_init.get_config_path', return_value=config_file):
        result = get_jira_credentials()

    assert result == ('https://test.atlassian.net', 'test@example.com', 'test-token')


def test_get_jira_credentials_missing(tmp_path: Path) -> None:
    config_file = tmp_path / 'credentials.json'

    with patch('standupbrain.jira_init.get_config_path', return_value=config_file):
        result = get_jira_credentials()

    assert result is None
