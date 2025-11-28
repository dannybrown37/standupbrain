import sys

from standupbrain.llm import init_llm


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: standupbrain <command>')
        sys.exit(1)

    command = sys.argv[1]

    if command == 'init':
        init_llm()
    else:
        print(f'Unknown command: {command}')
        sys.exit(1)
