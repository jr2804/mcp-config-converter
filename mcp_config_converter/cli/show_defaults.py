"""Show default output paths for providers."""

from __future__ import annotations

from rich.table import Table

from mcp_config_converter.cli import app, console
from mcp_config_converter.cli.constants import PROVIDER_DEFAULT_OUTPUT_FILES
from mcp_config_converter.types import PROVIDER_ALIAS_MAP, ProviderConfig


def _alias_of(provider: str) -> str:
    """Return alias target for provider or '-' if none."""
    try:
        provider_key: ProviderConfig | str = ProviderConfig(provider)
    except ValueError:
        provider_key = provider

    alias = PROVIDER_ALIAS_MAP.get(provider_key) or PROVIDER_ALIAS_MAP.get(provider)
    if alias is None:
        return "-"
    if isinstance(alias, ProviderConfig):
        return alias.value
    return str(alias)


@app.command(name="show-defaults")
def show_defaults() -> None:
    """Display default output paths for all providers."""
    table = Table(title="Default Output Paths", show_header=True, header_style="bold magenta")
    table.add_column("Output Provider", style="cyan", no_wrap=True)
    table.add_column("Default Output Path", style="green")
    table.add_column("Is Alias Of", style="yellow")

    for provider, path in PROVIDER_DEFAULT_OUTPUT_FILES.items():
        table.add_row(str(provider), str(path), _alias_of(provider))

    console.print(table)
