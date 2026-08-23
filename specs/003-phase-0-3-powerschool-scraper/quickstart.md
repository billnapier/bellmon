# Quickstart & Testing Guide: Micro-Spec 0.3

**Feature Branch**: `003-phase-0-3-powerschool-scraper`

## Executing Unit & Integration Tests

Run the test suite via `pytest`:

```bash
pytest tests/test_powerschool.py -v
```

## Scraper Usage Example

```python
from src.ingestion.powerschool import PowerSchoolScraper

scraper = PowerSchoolScraper(student_id="student_123")
result = scraper.run_ingestion()

print(f"Courses extracted: {len(result['courses'])}")
print(f"Attendance records extracted: {len(result['attendance'])}")
```
