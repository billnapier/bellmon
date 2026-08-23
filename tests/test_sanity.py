"""
Sanity tests for Bellmon runtime initialization.
"""

from unittest.mock import patch
from src.main import main, StudentSnapshot, BatchExecutionResult


@patch("src.main.run_batch")
def test_main_execution(mock_run_batch):
    """Verify that main execution entrypoint completes with exit code 0."""
    mock_result = BatchExecutionResult(
        timestamp="2026-08-23T00:00:00Z",
        status="SUCCESS",
        canvas_status="SUCCESS",
        powerschool_status="SUCCESS",
        duration_seconds=0.1
    )
    mock_snapshot = StudentSnapshot(student_id="test", timestamp="2026-08-23T00:00:00Z")
    mock_run_batch.return_value = (mock_snapshot, mock_result)

    result = main()
    assert result == 0
