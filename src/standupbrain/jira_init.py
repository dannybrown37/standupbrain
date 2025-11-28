import click
import keyring
from typing import TypedDict


class JiraConfig(TypedDict):
    root_url: str
    email: str


def init_jira() -> JiraConfig:
    click.echo('Setting up Jira integration...\n')

    root_url = click.prompt(
        'Jira root URL (e.g., https://yourcompany.atlassian.net)',
        type=str,
    ).rstrip('/')

    email = click.prompt('Jira email', type=str)

    api_token = click.prompt(
        'Jira API token (https://id.atlassian.com/manage-profile/security/api-tokens)',
        hide_input=True,
    )

    if click.confirm('\nSave credentials securely?', default=True):
        keyring.set_password('jira_cli', 'root_url', root_url)
        keyring.set_password('jira_cli', 'email', email)
        keyring.set_password('jira_cli', 'api_token', api_token)
        click.echo('✓ Credentials saved')

    return {'root_url': root_url, 'email': email}
