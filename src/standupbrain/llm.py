import shutil
import subprocess
import sys
from pathlib import Path
import time


def init_llm() -> None:
    if not check_ollama_installed():
        print('Ollama not found. Attempting installation...')
        if not install_ollama():
            print(
                'Failed to install Ollama automatically.\n'
                'Please install manually: https://ollama.com/download'
            )
            sys.exit(1)
        print('Ollama installed successfully.')

    if not ensure_ollama_running():
        sys.exit(1)

    if not pull_model():
        print('Failed to pull model.')
        sys.exit(1)

    print('LLM setup complete.')


def check_ollama_installed() -> bool:
    return shutil.which('ollama') is not None


def ensure_ollama_running() -> bool:
    try:
        subprocess.run(['ollama', 'list'], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        print('Starting Ollama server...')
        print('Starting Ollama server...')
        proc = subprocess.Popen(
            ['ollama', 'serve'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(3)
        print(proc.stderr.read() if proc.stderr else 'No stderr')

        for _ in range(10):
            time.sleep(1)
            try:
                subprocess.run(
                    ['ollama', 'list'], check=True, capture_output=True
                )
                return True
            except subprocess.CalledProcessError:
                continue

        print('Failed to start Ollama server')
        return False


def install_ollama() -> bool:
    if sys.platform == 'darwin':
        print('Installing Ollama via Homebrew...')
        try:
            subprocess.run(['brew', 'install', 'ollama'], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    elif sys.platform.startswith('linux'):
        print('Installing Ollama via official script...')
        try:
            subprocess.run(
                ['curl', '-fsSL', 'https://ollama.com/install.sh'],
                stdout=subprocess.PIPE,
                check=True,
            )
            subprocess.run(['sh', '-'], input=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        return False


def pull_model(model: str = 'qwen2.5:3b') -> bool:
    print(f'Pulling {model}...')
    try:
        subprocess.run(['ollama', 'pull', model], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
