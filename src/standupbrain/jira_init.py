import json

import click

from standupbrain.shared import get_config_path


def init_jira() -> None:
    click.echo('Setting up Jira integration...\n')
    credentials = get_jira_credentials()
    url, email, api_token = None, None, None
    if credentials:
        click.echo(f'✓ Jira credentials already set for {credentials[1]}')
        if not click.confirm('Review/overwrite existing credentials?', default=False):
            click.echo('Keeping existing credentials')
            return
        url, email, api_token = credentials

    root_url = (
        click.prompt(
            'Jira root URL (e.g., https://yourcompany.atlassian.net)',
            type=str,
            default=url,
        )
        .rstrip('/')
        .strip()
    )

    email = click.prompt('Jira email', type=str, default=email).strip()

    api_token = click.prompt(
        'Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens)',
        default=api_token,
    ).strip()

    if click.confirm('\nSave credentials?', default=True):
        config_path = get_config_path()
        config_path.write_text(
            json.dumps(
                {
                    'root_url': root_url,
                    'email': email,
                    'api_token': api_token,
                },
            ),
        )
        config_path.chmod(0o600)
        click.echo(f'✓ Saved to {config_path}')


def get_jira_credentials() -> tuple[str, str, str] | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    data = json.loads(config_path.read_text())
    url, email, token = data.get('root_url'), data.get('email'), data.get('api_token')
    if url is None or email is None or token is None:
        return None
    return url, email, token
