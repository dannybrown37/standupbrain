import json
import logging
import shutil
import subprocess
import sys
import time

import click

from standupbrain.shared import OLLAMA_MODEL, get_config_path, get_preferences

log = logging.getLogger(__name__)


def init_llm() -> None:
    if not check_ollama_installed():
        log.info('Ollama not found. Attempting installation...')
        if not install_ollama():
            log.info(
                'Failed to install Ollama automatically.\n'
                'Please install manually: https://ollama.com/download',
            )
            sys.exit(1)
        log.info('Ollama installed successfully.')

    if not ensure_ollama_running():
        log.error('Failed to start Ollama server.')
        sys.exit(1)

    if not init_preferences():
        log.error('Failed to set preferences.')
        sys.exit(1)

    if not pull_model():
        log.error('Failed to pull model.')
        sys.exit(1)

    log.info('LLM setup complete.')


def check_ollama_installed() -> bool:
    return shutil.which('ollama') is not None


def ensure_ollama_running() -> bool:
    try:
        subprocess.run(['ollama', 'list'], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        log.info('Starting Ollama server...')
        subprocess.Popen(
            ['ollama', 'serve'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(10):
            time.sleep(1)
            try:
                subprocess.run(
                    ['ollama', 'list'],
                    check=True,
                    capture_output=True,
                )
                return True
            except subprocess.CalledProcessError:
                continue

        log.info('Failed to start Ollama server')
        return False


def install_ollama() -> bool:
    if sys.platform == 'darwin':
        log.info('Installing Ollama via Homebrew...')
        try:
            subprocess.run(['brew', 'install', 'ollama'], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    elif sys.platform.startswith('linux'):
        log.info('Installing Ollama via official script...')
        try:
            result = subprocess.run(
                ['curl', '-fsSL', 'https://ollama.com/install.sh'],
                capture_output=True,
                check=True,
            )
            subprocess.run(['sh', '-'], input=result.stdout, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False


def pull_model(model: str = OLLAMA_MODEL) -> bool:
    log.info('Pulling %s...', model)
    try:
        subprocess.run(['ollama', 'pull', model], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_available_ollama_models() -> list[dict[str, str]]:
    result = subprocess.run(
        ['ollama', 'list'],
        capture_output=True,
        text=True,
        check=True,
    )
    models = []
    for line in result.stdout.strip().split('\n')[1:]:
        parts = line.split()
        if parts:
            models.append({'name': parts[0], 'size': parts[2]})
    return models


def init_preferences() -> bool:
    click.echo('Setting up preferences...\n')
    preferences = get_preferences()
    ollama_model = None
    if preferences:
        click.echo(f'✓ Preferences already set (model: {preferences["ollama_model"]})')
        if not click.confirm('Review/overwrite existing preferences?', default=False):
            click.echo('Keeping existing preferences')
            return False
        ollama_model = preferences['ollama_model']

    models = get_available_ollama_models()
    if not models:
        click.echo(
            '⚠ No Ollama models found. Pull a model first with: ollama pull <model>',
        )
        return False

    click.echo('Available models:')
    for idx, model in enumerate(models, 1):
        click.echo(f'  {idx}. {model["name"]} ({model["size"]})')

    choice = click.prompt(
        '\nSelect model number',
        type=click.IntRange(1, len(models)),
        default=1,
    )
    ollama_model = models[choice - 1]['name']

    if click.confirm(f'\nSave {ollama_model} as default?', default=True):
        config_path = get_config_path()
        existing = {}
        if config_path.exists():
            existing = json.loads(config_path.read_text())

        existing['ollama_model'] = ollama_model

        config_path.write_text(json.dumps(existing))
        config_path.chmod(0o600)
        click.echo(f'✓ Saved to {config_path}')
    return True
