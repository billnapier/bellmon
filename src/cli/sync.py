import argparse
import asyncio
import sys
from datetime import datetime, timezone
from src.config import settings
from src.harvesters.canvas import CanvasHarvester
from src.harvesters.powerschool import PowerSchoolHarvester
from src.storage.firestore import FirestoreStore
from src.storage.models import Student, CourseSnapshot
from src.engine.grace_period import GracePeriodEvaluator
from src.engine.missing_work import MissingWorkEvaluator
from src.engine.velocity import VelocityDropEvaluator
from src.engine.attendance import AttendanceEvaluator
from src.engine.clumping import WorkloadClumpingRadar
from src.router.push import PushRouter
from src.router.email import EmailDigestRouter


async def run_sentinel_sync(student_id: str, dry_run: bool = False, is_sunday_digest: bool = False) -> int:
    print(f"=== Starting Bellmon Sentinel Sync Run for Student: {student_id} (Dry Run: {dry_run}) ===")
    
    # 1. Initialize Clients
    canvas = CanvasHarvester()
    powerschool = PowerSchoolHarvester()
    store = FirestoreStore()
    push_router = PushRouter()
    email_router = EmailDigestRouter()

    grace_evaluator = GracePeriodEvaluator()
    missing_evaluator = MissingWorkEvaluator()
    velocity_evaluator = VelocityDropEvaluator()
    attendance_evaluator = AttendanceEvaluator()
    clumping_radar = WorkloadClumpingRadar()

    # 2. Ingest Data
    canvas_missing = await canvas.fetch_missing_assignments(student_id)
    ps_courses, ps_attendance = await powerschool.fetch_student_data(student_id)

    # Historical state
    previous_snapshot = store.load_student(student_id)

    print(f"Ingested {len(canvas_missing)} Canvas missing items & {len(ps_courses)} PowerSchool course snapshots.")

    # 3. Evaluate Rule Matrix
    alert_count = 0
    for assignment in canvas_missing:
        # Cross-system missing work check
        assignment, missing_alert, reason = missing_evaluator.evaluate(assignment)
        if missing_alert:
            alert_id = f"{student_id}_{assignment.assignment_id}_missing"
            if not dry_run:
                await push_router.send_p0_alert(
                    alert_id=alert_id,
                    student_id=student_id,
                    title=f"🚨 Confirmed Missing Work: {assignment.title}",
                    message=f"Assignment '{assignment.title}' is marked missing in PowerSchool.",
                    assignment_id=assignment.assignment_id
                )
            print(f"[ALERT] Confirmed Missing: {assignment.title} ({reason})")
            alert_count += 1
            continue

        # Grace Period evaluation
        assignment, grace_alert = grace_evaluator.evaluate(assignment)
        if grace_alert:
            alert_id = f"{student_id}_{assignment.assignment_id}_grace_expired"
            if not dry_run:
                await push_router.send_p0_alert(
                    alert_id=alert_id,
                    student_id=student_id,
                    title=f"⏰ Grace Period Expired: {assignment.title}",
                    message=f"Digital submission '{assignment.title}' remains overdue past the 36h grace period.",
                    assignment_id=assignment.assignment_id
                )
            print(f"[ALERT] Grace Period Expired: {assignment.title}")
            alert_count += 1

    # 4. Evaluate Attendance Anomalies
    for event in ps_attendance:
        should_alert, title, msg = attendance_evaluator.evaluate(event)
        if should_alert:
            alert_id = f"{student_id}_att_{event.event_id}"
            if not dry_run:
                await push_router.send_p0_alert(
                    alert_id=alert_id,
                    student_id=student_id,
                    title=title,
                    message=msg
                )
            print(f"[ALERT] Attendance Anomaly: {event.code}")
            alert_count += 1

    # 5. Evaluate Grade Velocity Drops
    if previous_snapshot:
        prev_course_map = {c.course_id: c for c in previous_snapshot.courses}
        for curr_c in ps_courses:
            hist_c = prev_course_map.get(curr_c.course_id)
            should_alert, drop, impacting = velocity_evaluator.evaluate(hist_c, curr_c)
            if should_alert:
                alert_id = f"{student_id}_{curr_c.course_id}_velocity_drop"
                impacting_title = impacting.title if impacting else "recent assignment"
                if not dry_run:
                    await push_router.send_p0_alert(
                        alert_id=alert_id,
                        student_id=student_id,
                        title=f"📉 Grade Velocity Drop: {curr_c.course_name} (-{drop}%)",
                        message=f"Course grade dropped {drop}% to {curr_c.current_score}%. Impacting item: {impacting_title}."
                    )
                print(f"[ALERT] Grade Drop: {curr_c.course_name} (-{drop}%)")
                alert_count += 1

    # 6. Save State Snapshot
    updated_student = Student(student_id=student_id, name="Alex Student", courses=ps_courses)
    if not dry_run:
        store.save_student(updated_student)

    # 7. Sunday Planning Digest
    if is_sunday_digest:
        clusters = clumping_radar.scan(ps_courses)
        html_digest = email_router.render_sunday_digest(updated_student, clusters)
        if not dry_run:
            await email_router.send_digest_email("parent@example.com", "Sunday Workload Digest", html_digest)
        print(f"[SUNDAY DIGEST] Rendered & sent digest with {len(clusters)} workload cluster warnings.")

    print(f"=== Sync Completed Successfully. Dispatched {alert_count} Alerts. ===")
    return alert_count


def main():
    parser = argparse.ArgumentParser(description="Bellmon Academic Sentinel CLI Sync Runner")
    parser.add_argument("--student-id", default="student_123", help="Student ID to run sync for")
    parser.add_argument("--dry-run", action="store_true", help="Run without persisting state or sending live notifications")
    parser.add_argument("--sunday-digest", action="store_true", help="Trigger Sunday planning digest build")

    args = parser.parse_args()
    asyncio.run(run_sentinel_sync(args.student_id, args.dry_run, args.sunday_digest))


if __name__ == "__main__":
    main()
