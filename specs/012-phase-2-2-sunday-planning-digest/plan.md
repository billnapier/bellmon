# Technical Plan: 012 Phase 2.2 Sunday Planning Digest

## Module Structure

```
src/
└── notifications/
    ├── digest.py       # SundayDigestPayload, SundayDigestRenderer, and SundayDigestRouter
tests/
└── test_sunday_digest.py  # Unit tests for digest rendering and scheduling
```

## Technical Specifications

### `SundayDigestRenderer`
- `render_html(payload: SundayDigestPayload) -> str`: Renders responsive HTML template with sections for Radar Warning (conditional), Course Standings, 7-Day Deadlines, and Attendance Summary.
- `render_text(payload: SundayDigestPayload) -> str`: Renders clean plain text email representation.

### `SundayDigestRouter`
- `should_send_digest(now: datetime, last_sent_at: Optional[datetime]) -> bool`: Evaluates if current time is Sunday >= 18:00 UTC and `last_sent_at` is older than 48 hours.

## Key Test Scenarios
1. **HTML & Text Template Generation**: Verify clean compilation of HTML/text output.
2. **Conditional Radar Banner**: Verify banner is present when `has_clumping == True` and absent when `has_clumping == False`.
3. **Schedule Verification**: Verify `should_send_digest()` returns True only on Sunday after 18:00 when last_sent_at is empty or > 48h ago.
4. **Attendance Summary Aggregation**: Verify accurate counting of `T` and `U` codes.
