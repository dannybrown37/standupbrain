import json
import click

from standupbrain.shared import get_config_path


def init_preferences() -> None:
    click.echo('Setting up preferences...\n')
    preferences = get_preferences()
    ollama_model = None
    if preferences:
        click.echo(f'✓ Preferences already set (model: {preferences["ollama_model"]})')
        if not click.confirm('Review/overwrite existing preferences?', default=False):
            click.echo('Keeping existing preferences')
            return
        ollama_model = preferences['ollama_model']

    ollama_model = click.prompt(
        'Ollama model',
        type=str,
        default=ollama_model or 'llama3.2:3b',
    ).strip()

    if click.confirm('\nSave preferences?', default=True):
        config_path = get_config_path()
        existing = {}
        if config_path.exists():
            existing = json.loads(config_path.read_text())

        existing['ollama_model'] = ollama_model

        config_path.write_text(json.dumps(existing))
        config_path.chmod(0o600)
        click.echo(f'✓ Saved to {config_path}')


def get_preferences() -> dict | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    data = json.loads(config_path.read_text())
    return data if 'ollama_model' in data else None
