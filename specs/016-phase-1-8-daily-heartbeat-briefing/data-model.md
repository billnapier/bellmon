# Data Model: Phase 1.8 Daily Heartbeat & System Activity Briefing

## Entities & Schemas

### 1. IngestionStatusRecord
Stored in Firestore collection: `ingestion_status/{date}`

```json
{
  "date": "2026-08-31",
  "sync_timestamp": "2026-08-31T17:00:00Z",
  "canvas_status": "OPERATIONAL",
  "powerschool_status": "OPERATIONAL",
  "error_details": null
}
```

### 2. GraceWatchlistItem
Value object representing an assignment in grace period.

```json
{
  "assignment_id": "canvas_101",
  "course_name": "AP Physics C",
  "title": "Lab Report 3",
  "due_at": "2026-08-30T23:59:00Z",
  "hours_remaining": 14.5
}
```

### 3. AttendancePeriodRecord
Value object representing attendance for a single period.

```json
{
  "period": "1",
  "course_name": "AP Physics C",
  "status": "PRESENT",
  "code": "P"
}
```

### 4. HeartbeatPayload
Main payload passed to renderer and router.

```json
{
  "student_name": "Alex Napier",
  "sync_timestamp": "2026-08-31T17:00:00Z",
  "canvas_status": "OPERATIONAL",
  "powerschool_status": "OPERATIONAL",
  "grace_watchlist": [
    {
      "assignment_id": "canvas_101",
      "course_name": "AP Physics C",
      "title": "Lab Report 3",
      "due_at": "2026-08-30T23:59:00Z",
      "hours_remaining": 14.5
    }
  ],
  "attendance_summary": {
    "total_periods": 6,
    "present_count": 6,
    "periods": [
      {"period": "1", "course_name": "AP Physics", "status": "PRESENT"},
      {"period": "2", "course_name": "Calculus BC", "status": "PRESENT"},
      {"period": "3", "course_name": "English Lit", "status": "PRESENT"},
      {"period": "4", "course_name": "US History", "status": "PRESENT"},
      {"period": "5", "course_name": "Chemistry", "status": "PRESENT"},
      {"period": "6", "course_name": "Spanish IV", "status": "PRESENT"}
    ]
  },
  "zero_alert_confirmed": true,
  "alerts_dispatched_today": 0
}
```

### 5. HeartbeatDispatchRecord
Stored in Firestore collection: `heartbeat_briefings/{student_id}_{date}`

```json
{
  "id": "alex_napier_2026-08-31",
  "student_name": "Alex Napier",
  "date": "2026-08-31",
  "dispatched_at": "2026-08-31T17:15:00Z",
  "recipient": "parent@example.com",
  "message_id": "msg_resend_999",
  "status": "SUCCESS"
}
```
