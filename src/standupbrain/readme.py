import subprocess
from pathlib import Path


def update_readme_with_help(
    cli_commands: list[list[str]],
    readme_path: Path = Path('README.md'),
) -> None:
    help_sections = []

    for cmd in cli_commands:
        result = subprocess.run(
            [*cmd, '--help'],
            capture_output=True,
            text=True,
            check=True,
        )
        cmd_str = ' '.join(cmd)
        help_sections.append(f'## `{cmd_str} --help`\n\n```bash\n{result.stdout}```')

    help_content = '\n\n'.join(help_sections)

    marker_start = '<!-- CLI_HELP_START -->'
    marker_end = '<!-- CLI_HELP_END -->'

    readme = readme_path.read_text()

    if marker_start in readme and marker_end in readme:
        before = readme.split(marker_start)[0]
        after = readme.split(marker_end)[1]
        updated = f'{before}{marker_start}\n{help_content}\n{marker_end}{after}'
    else:
        updated = f'{readme}\n\n{marker_start}\n{help_content}\n{marker_end}\n'

    readme_path.write_text(updated)


if __name__ == '__main__':
    update_readme_with_help(
        [
            ['standupbrain'],
            ['standupbrain', 'init'],
            ['standupbrain', 'recall'],
        ],
    )
