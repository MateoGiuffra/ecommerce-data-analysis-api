"""Re-export of the Typer CLI from the src package.

This allows the console script to point to
`ecommerce_data_analysis_api.cli:app` which is installable by Poetry.
"""
from src.cli import app

__all__ = ["app"]
