import logging
import shutil
import subprocess
import sys
import time

from standupbrain.shared import OLLAMA_MODEL

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
        sys.exit(1)

    if not pull_model():
        log.info('Failed to pull model.')
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
