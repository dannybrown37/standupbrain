from pathlib import Path
import json

import click


def get_config_path() -> Path:
    config_dir = Path.home() / '.config' / 'standupbrain'
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'credentials.json'


def init_jira() -> None:
    click.echo('Setting up Jira integration...\n')

    root_url = click.prompt(
        'Jira root URL (e.g., https://yourcompany.atlassian.net)',
        type=str,
    ).rstrip('/').strip()

    email = click.prompt('Jira email', type=str).strip()

    api_token = click.prompt(
        'Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens)',
        hide_input=True,
    ).strip()

    if click.confirm('\nSave credentials?', default=True):
        config_path = get_config_path()
        config_path.write_text(json.dumps({
            'root_url': root_url,
            'email': email,
            'api_token': api_token,
        }))
        config_path.chmod(0o600)
        click.echo(f'✓ Saved to {config_path}')

    return {'root_url': root_url, 'email': email}


def get_jira_credentials() -> tuple[str, str, str] | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    data = json.loads(config_path.read_text())
    return data['root_url'], data['email'], data['api_token']
