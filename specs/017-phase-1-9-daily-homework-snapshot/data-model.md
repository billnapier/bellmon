# Data Model: Phase 1.9 Daily Evening Homework & Deadline Snapshot

## Data Structures

### `UpcomingDeadlineItem`
- `assignment_id` (str): Unique ID of assignment.
- `title` (str): Title of assignment.
- `course` (str): Name or code of course.
- `due_at` (datetime): Due date and time.
- `portal` (str): Origin portal (`Canvas` or `PowerSchool`).
- `submitted` (bool): `True` if submitted, `False` otherwise.
- `submission_url` (Optional[str]): Direct link to submit in portal.

### `GracePeriodSnapshotItem`
- `assignment_id` (str): Unique ID of assignment.
- `title` (str): Title of assignment.
- `course` (str): Name or code of course.
- `original_due_at` (datetime): Original due timestamp.
- `hours_remaining` (float): Hours left in 36-hour grace period window.
- `portal` (str): Origin portal (`Canvas` or `PowerSchool`).
- `submission_url` (Optional[str]): Direct link to submit.

### `RecentlyCompletedItem`
- `assignment_id` (str): Unique ID of assignment.
- `title` (str): Title of assignment.
- `course` (str): Name or code of course.
- `submitted_at` (datetime): Submission timestamp.
- `portal` (str): Origin portal.

### `HomeworkSnapshotPayload`
- `generated_at` (datetime): Snapshot generation timestamp.
- `student_id` (str): ID of student.
- `student_name` (str): Display name of student.
- `upcoming_deadlines` (List[UpcomingDeadlineItem]): Sorted chronologically by `due_at`.
- `grace_period_items` (List[GracePeriodSnapshotItem]): Active grace period items.
- `recently_completed` (List[RecentlyCompletedItem]): Assignments submitted in past 24 hours.

---

## Firestore Collection: `homework_snapshots`

Document Key: `{student_id}:{YYYY-MM-DD}`

Document Fields:
- `student_id` (string)
- `dispatch_date` (string `YYYY-MM-DD`)
- `dispatched_at` (iso string)
- `recipient_email` (string)
- `status` (string: `SENT`, `SKIPPED`, `FAILED`)
- `upcoming_count` (int)
- `grace_count` (int)
- `completed_count` (int)
