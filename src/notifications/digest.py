"""Sunday Evening Weekly Planning Digest Module (Spec 012)."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.radar.models import WorkloadRadarResult


class SundayDigestPayload(BaseModel):
    """Payload data required to render the Sunday Evening Digest email."""

    student_name: str
    digest_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    course_standings: List[Dict[str, Any]] = Field(default_factory=list)
    workload_radar: Optional[WorkloadRadarResult] = None
    upcoming_deadlines: List[Dict[str, Any]] = Field(default_factory=list)
    attendance_records: List[Dict[str, Any]] = Field(default_factory=list)
    tardy_count: int = 0
    unverified_count: int = 0


class SundayDigestRenderer:
    """Renders HTML and Text templates for the Sunday Evening Digest email."""

    def render_html(self, payload: SundayDigestPayload) -> str:
        date_str = payload.digest_date.strftime("%B %d, %Y")

        # Section 1: Radar Warning Banner
        radar_html = ""
        if payload.workload_radar and payload.workload_radar.has_clumping:
            cluster_items_html = ""
            for cluster in payload.workload_radar.clusters:
                courses_str = ", ".join(cluster.courses)
                item_names = ", ".join([item.title for item in cluster.assessments])
                start_str = cluster.start_time.strftime("%a %b %d")
                cluster_items_html += f"""
                <div style="background:#fff3cd; border-left:4px solid #ffc107; padding:10px; margin-bottom:8px; border-radius:4px;">
                    <strong>Workload Spike ({start_str}):</strong> {cluster.total_major_items} major assessments in {courses_str}<br/>
                    <small style="color:#666;">Assessments: {item_names}</small>
                </div>
                """
            radar_html = f"""
            <div style="margin-bottom:24px;">
                <h3 style="color:#d9534f; margin-bottom:8px;">⚠️ Workload Clumping Radar Alert</h3>
                {cluster_items_html}
            </div>
            """

        # Section 2: Course Standings
        courses_rows = ""
        for course in payload.course_standings:
            c_name = course.get("course_name", "Unknown")
            letter = course.get("grade_letter", "N/A")
            percent = course.get("grade_percent", 0.0)
            teacher = course.get("teacher_name", "N/A")
            courses_rows += f"""
            <tr>
                <td style="padding:8px; border-bottom:1px solid #eee;"><strong>{c_name}</strong></td>
                <td style="padding:8px; border-bottom:1px solid #eee;">{letter} ({percent:.1f}%)</td>
                <td style="padding:8px; border-bottom:1px solid #eee; color:#666;">{teacher}</td>
            </tr>
            """

        standings_html = f"""
        <div style="margin-bottom:24px;">
            <h3 style="color:#2b3a4a; margin-bottom:8px;">📚 Current Academic Standings</h3>
            <table style="width:100%; border-collapse:collapse; text-align:left;">
                <thead>
                    <tr style="background:#f4f6f8;">
                        <th style="padding:8px; border-bottom:2px solid #ddd;">Course</th>
                        <th style="padding:8px; border-bottom:2px solid #ddd;">Grade</th>
                        <th style="padding:8px; border-bottom:2px solid #ddd;">Teacher</th>
                    </tr>
                </thead>
                <tbody>
                    {courses_rows if courses_rows else '<tr><td colspan="3" style="padding:8px;">No course data available.</td></tr>'}
                </tbody>
            </table>
        </div>
        """

        # Section 3: Upcoming Deadlines
        deadlines_rows = ""
        for item in payload.upcoming_deadlines:
            title = item.get("title", "Untitled")
            course = item.get("course_name", "")
            due_at = item.get("due_at", "")
            pts = item.get("points_possible", 0)
            deadlines_rows += f"""
            <li style="margin-bottom:6px;">
                <strong>{title}</strong> ({course}) — Due: {due_at} [{pts} pts]
            </li>
            """

        deadlines_html = f"""
        <div style="margin-bottom:24px;">
            <h3 style="color:#2b3a4a; margin-bottom:8px;">📅 Upcoming 7-Day Deadlines</h3>
            <ul style="padding-left:20px; margin:0;">
                {deadlines_rows if deadlines_rows else '<li style="color:#666;">No upcoming deadlines scheduled for the next 7 days.</li>'}
            </ul>
        </div>
        """

        # Section 4: Attendance Summary
        attendance_html = f"""
        <div style="margin-bottom:24px;">
            <h3 style="color:#2b3a4a; margin-bottom:8px;">⏱️ Weekly Attendance Summary</h3>
            <p style="margin:4px 0;">Tardies logged past 7 days: <strong>{payload.tardy_count}</strong></p>
            <p style="margin:4px 0;">Unverified absences logged past 7 days: <strong>{payload.unverified_count}</strong></p>
        </div>
        """

        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><title>Bellmon Sunday Planning Digest</title></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color:#f9fafb; margin:0; padding:20px;">
    <div style="max-width:600px; margin:0 auto; background:#ffffff; border:1px solid #e5e7eb; border-radius:8px; padding:24px;">
        <div style="text-align:center; border-bottom:2px solid #2563eb; padding-bottom:16px; margin-bottom:20px;">
            <h1 style="color:#1e3a8a; margin:0; font-size:22px;">Bellmon Weekly Planning Digest</h1>
            <p style="color:#6b7280; margin:4px 0 0 0;">Student: <strong>{payload.student_name}</strong> | Date: {date_str}</p>
        </div>
        {radar_html}
        {standings_html}
        {deadlines_html}
        {attendance_html}
        <div style="border-top:1px solid #e5e7eb; padding-top:12px; font-size:12px; color:#9ca3af; text-align:center;">
            Bellmon Sentinel Academic & Attendance System &bull; Generated Automatically
        </div>
    </div>
</body>
</html>"""
        return html

    def render_text(self, payload: SundayDigestPayload) -> str:
        date_str = payload.digest_date.strftime("%B %d, %Y")
        lines = [
            "==================================================",
            f"BELLMON WEEKLY PLANNING DIGEST - {payload.student_name}",
            f"Date: {date_str}",
            "==================================================",
            "",
        ]

        if payload.workload_radar and payload.workload_radar.has_clumping:
            lines.append("*** WORKLOAD CLUMPING RADAR WARNING ***")
            for cluster in payload.workload_radar.clusters:
                lines.append(f"- Spike on {cluster.start_time.strftime('%a %b %d')}: {cluster.total_major_items} major items in {', '.join(cluster.courses)}")
            lines.append("")

        lines.append("CURRENT ACADEMIC STANDINGS:")
        for c in payload.course_standings:
            lines.append(f"- {c.get('course_name')}: {c.get('grade_letter')} ({c.get('grade_percent')}%) - Teacher: {c.get('teacher_name')}")
        lines.append("")

        lines.append("UPCOMING 7-DAY DEADLINES:")
        if payload.upcoming_deadlines:
            for item in payload.upcoming_deadlines:
                lines.append(f"- {item.get('title')} ({item.get('course_name')}) Due: {item.get('due_at')}")
        else:
            lines.append("- No upcoming deadlines.")
        lines.append("")

        lines.append("WEEKLY ATTENDANCE SUMMARY:")
        lines.append(f"- Tardies (past 7 days): {payload.tardy_count}")
        lines.append(f"- Unverified Absences (past 7 days): {payload.unverified_count}")
        lines.append("")
        lines.append("==================================================")
        return "\n".join(lines)


class SundayDigestRouter:
    """Evaluates whether to dispatch the Sunday Evening Digest based on time and deduplication rules."""

    def should_send_digest(
        self,
        now: Optional[datetime] = None,
        last_sent_at: Optional[datetime] = None,
    ) -> bool:
        if now is None:
            now = datetime.now(timezone.utc)
        elif now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Must be Sunday (weekday 6) and hour >= 18 (6:00 PM)
        if now.weekday() != 6 or now.hour < 18:
            return False

        # Check deduplication window (48 hours)
        if last_sent_at is not None:
            if last_sent_at.tzinfo is None:
                last_sent_at = last_sent_at.replace(tzinfo=timezone.utc)
            elapsed = (now - last_sent_at).total_seconds() / 3600.0
            if elapsed < 48.0:
                return False

        return True
