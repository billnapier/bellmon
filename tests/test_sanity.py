"""
Sanity tests for Bellmon runtime initialization.
"""

from src.main import main


def test_main_execution():
    """Verify that main execution entrypoint completes with exit code 0."""
    result = main()
    assert result == 0
