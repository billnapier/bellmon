import pytest
from src.cli.sync import run_sentinel_sync


@pytest.mark.asyncio
async def test_end_to_end_sentinel_sync_dry_run():
    # Dry run execution should complete with 0 errors and return dispatched alert count
    alerts_dispatched = await run_sentinel_sync(student_id="test_student_e2e", dry_run=True, is_sunday_digest=True)
    assert isinstance(alerts_dispatched, int)
    assert alerts_dispatched >= 0
