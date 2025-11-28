import click

from standupbrain.llm import init_llm


@click.group()
def main() -> None:
    pass


@main.command()
def init() -> None:
    init_llm()
