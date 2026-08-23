# Data Models & Entities: Micro-Spec 0.3

**Feature Branch**: `003-phase-0-3-powerschool-scraper`

## Core Entities

### 1. `PowerSchoolCourse`
Represents an enrolled course in PowerSchool SIS.

| Field | Type | Description |
|---|---|---|
| `course_code` | `str` | Official course identifier code (e.g., `MATH301`) |
| `name` | `str` | Course display title (e.g., `AP Calculus BC`) |
| `letter_grade` | `str` | Current letter grade (e.g., `A`, `B+`, `N/A`) |
| `percentage` | `float` | Current numerical percentage grade (e.g., `95.5`) |

### 2. `AttendanceRecord`
Represents a specific period-level attendance event or code.

| Field | Type | Description |
|---|---|---|
| `date` | `str` | Attendance event date (`YYYY-MM-DD`) |
| `period` | `str` | Class period designation (e.g., `P1`, `P2`) |
| `course` | `str` | Associated course name or code |
| `code` | `str` | Attendance code (`A` = Absent, `CUT` = Cut, `T` = Tardy, `U` = Unexcused) |

### 3. `SessionCookieStore`
Represents persisted cookie payload stored in Firestore under `students/{student_id}`.

| Field | Type | Description |
|---|---|---|
| `psaid` | `str` | PowerSchool session authentication cookie value |
| `updated_at` | `str` | ISO 8601 UTC timestamp of last cookie refresh |
