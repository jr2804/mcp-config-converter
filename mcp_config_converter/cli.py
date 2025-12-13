"""Main CLI entry point for MCP Config Converter."""

import click
from pathlib import Path
from typing import Optional


@click.group()
@click.version_option()
def cli():
    """MCP Config Converter - Convert MCP configurations between formats and LLM providers."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'toml']),
              help='Output format')
@click.option('--provider', '-p', type=click.Choice(['claude', 'gemini', 'vscode', 'opencode']),
              help='Target LLM provider')
def convert(input_file: str, output: Optional[str], format: Optional[str], provider: Optional[str]):
    """Convert MCP configuration from one format to another."""
    click.echo(f"Converting {input_file}...")
    if format:
        click.echo(f"Target format: {format}")
    if provider:
        click.echo(f"Target provider: {provider}")
    if output:
        click.echo(f"Output file: {output}")


@cli.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate(config_file: str):
    """Validate an MCP configuration file."""
    click.echo(f"Validating {config_file}...")


@cli.command()
def init():
    """Initialize a new MCP configuration."""
    click.echo("Initializing new MCP configuration...")


if __name__ == '__main__':
    cli()
