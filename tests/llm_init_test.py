import subprocess
from unittest.mock import MagicMock, patch

import pytest

from standupbrain.llm_init import (
    check_ollama_installed,
    install_ollama,
    pull_model,
)


def test_check_ollama_installed_when_found() -> None:
    with patch('standupbrain.llm_init.shutil.which', return_value='/usr/bin/ollama'):
        assert check_ollama_installed() is True


def test_check_ollama_installed_when_not_found() -> None:
    with patch('standupbrain.llm_init.shutil.which', return_value=None):
        assert check_ollama_installed() is False


@pytest.mark.parametrize(
    ('platform', 'should_succeed'),
    [
        ('darwin', True),
        ('linux', True),
        ('win32', False),
    ],
)
def test_install_ollama(platform: str, should_succeed: bool) -> None:
    with (
        patch('standupbrain.llm_init.sys.platform', platform),
        patch('standupbrain.llm_init.subprocess.run') as mock_run,
    ):
        result = install_ollama()
        assert result is should_succeed
        if should_succeed:
            assert mock_run.called


def test_install_ollama_darwin_failure() -> None:
    with (
        patch('standupbrain.llm_init.sys.platform', 'darwin'),
        patch(
            'standupbrain.llm_init.subprocess.run',
            side_effect=FileNotFoundError,
        ),
    ):
        assert install_ollama() is False


def test_install_ollama_linux_curl_failure() -> None:
    with (
        patch('standupbrain.llm_init.sys.platform', 'linux'),
        patch(
            'standupbrain.llm_init.subprocess.run',
            side_effect=subprocess.CalledProcessError(1, 'curl'),
        ),
    ):
        assert install_ollama() is False


@pytest.mark.parametrize(
    ('side_effect', 'expected'),
    [
        (None, True),
        (subprocess.CalledProcessError(1, 'ollama'), False),
    ],
)
def test_pull_model(side_effect: Exception | None, expected: bool) -> None:
    with patch('standupbrain.llm_init.subprocess.run', side_effect=side_effect):
        assert pull_model('llama2') is expected
