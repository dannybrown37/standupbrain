import json
import subprocess

import click

from standupbrain.shared import get_config_path


def init_git() -> None:
    click.echo('Setting up Git/GitHub configuration...\n')
    credentials = get_git_credentials()
    git_email, gh_username = None, None

    if credentials:
        click.echo(f'✓ Git config already set for {credentials[0]} / {credentials[1]}')
        if not click.confirm('Review/overwrite existing config?', default=False):
            click.echo('Keeping existing config')
            return
        git_email, gh_username = credentials
    else:
        git_email = get_local_git_email()
        gh_username = get_remote_gh_username()

    git_email = click.prompt('Git author email', type=str, default=git_email).strip()
    gh_username = click.prompt('GitHub username', type=str, default=gh_username).strip()

    click.echo(f'\n\nGit author email: {git_email}')
    click.echo(f'GitHub username: {gh_username}')

    if click.confirm('\nSave configuration?', default=True):
        config_path = get_config_path()
        existing_config = {}
        if config_path.exists():
            existing_config = json.loads(config_path.read_text())

        existing_config.update(
            {
                'git_email': git_email,
                'gh_username': gh_username,
            },
        )

        config_path.write_text(json.dumps(existing_config))
        config_path.chmod(0o600)
        click.echo(f'✓ Saved to {config_path}')


def get_git_credentials() -> tuple[str, str] | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    data = json.loads(config_path.read_text())
    if 'git_email' not in data or 'gh_username' not in data:
        return None

    return data['git_email'], data['gh_username']


def get_local_git_email() -> str | None:
    try:
        result = subprocess.run(
            ['git', 'config', 'user.email'],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() or None
    except FileNotFoundError:
        return None


def get_remote_gh_username() -> str | None:
    try:
        result = subprocess.run(
            ['gh', 'api', 'user', '--jq', '.login'],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() or None
    except FileNotFoundError:
        return None
