import datetime
import subprocess


def get_git_commits(date: datetime) -> str:
    result = subprocess.run(
        [
            'git',
            'log',
            f'--since={date} 00:00',
            f'--until={date} 23:59',
            '--author=danny',
            '--patch',
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout
