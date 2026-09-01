import click
from .collect import collect
from .train import train
from .infer import infer

@click.group()
def cli():
    """LLM Business Tuner - utility for fine-tuning on business interviews."""
    pass

cli.add_command(collect)
cli.add_command(train)
cli.add_command(infer)

if __name__ == "__main__":
    cli()
