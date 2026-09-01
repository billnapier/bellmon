"""
Responsive HTML Email Template Compiler for P0 Academic & Attendance Alerts.
"""

from typing import List, Any, Tuple
from html import escape


class NotificationRenderer:
    """Compiles aggregated P0 alert telemetry into responsive HTML and plaintext emails."""

    def compile_p0_email(
        self,
        student_name: str,
        missing_work: List[Any] = None,
        grade_drops: List[Any] = None,
        attendance_anomalies: List[Any] = None,
    ) -> Tuple[str, str]:
        """
        Renders responsive single-column HTML email body and plaintext fallback.

        Args:
            student_name: Name of the student.
            missing_work: List of confirmed missing work assignment objects or dicts.
            grade_drops: List of grade velocity drop objects or dicts.
            attendance_anomalies: List of attendance anomaly event objects or dicts.

        Returns:
            Tuple of (html_body, text_fallback)
        """
        missing_work = missing_work or []
        grade_drops = grade_drops or []
        attendance_anomalies = attendance_anomalies or []

        # Build Plaintext Version
        text_lines = [
            f"BELLMON ACADEMIC SENTINEL - URGENT P0 ALERTS",
            f"Student: {student_name}",
            f"=" * 50,
            "",
        ]

        if missing_work:
            text_lines.append(f"[!] CONFIRMED MISSING WORK ({len(missing_work)} item(s)):")
            for item in missing_work:
                title = getattr(item, "assignment_name", None) or getattr(item, "title", str(item))
                course = getattr(item, "course_name", None) or getattr(item, "course_id", None) or getattr(item, "course", "Course")
                due = getattr(item, "due_at", None) or getattr(item, "due_date", "N/A")
                text_lines.append(f"  - {course}: {title} (Due: {due})")
            text_lines.append("")

        if grade_drops:
            text_lines.append(f"[!] GRADE VELOCITY DROPS ({len(grade_drops)} item(s)):")
            for item in grade_drops:
                course = getattr(item, "course_name", None) or getattr(item, "course", "Course")
                previous = getattr(item, "previous_score", None) if getattr(item, "previous_score", None) is not None else (getattr(item, "prev_percentage", None) if getattr(item, "prev_percentage", None) is not None else getattr(item, "previous_grade", "N/A"))
                current = getattr(item, "current_score", None) if getattr(item, "current_score", None) is not None else (getattr(item, "curr_percentage", None) if getattr(item, "curr_percentage", None) is not None else getattr(item, "current_grade", "N/A"))
                text_lines.append(f"  - {course}: Drop from {previous}% to {current}%")
            text_lines.append("")

        if attendance_anomalies:
            text_lines.append(f"[!] ATTENDANCE ANOMALIES ({len(attendance_anomalies)} item(s)):")
            for item in attendance_anomalies:
                code = getattr(item, "code", "UNEXCUSED")
                date = getattr(item, "date", "Today")
                period = getattr(item, "period", "N/A")
                desc = getattr(item, "description", "Unexcused Absence/Cut")
                text_lines.append(f"  - {date} Period {period} [{code}]: {desc}")
            text_lines.append("")

        text_lines.append("Please log into the student portal to review these alerts.")
        text_fallback = "\n".join(text_lines)

        # Build Responsive HTML Version
        html_sections = []

        if missing_work:
            items_html = ""
            for item in missing_work:
                title = escape(str(getattr(item, "assignment_name", None) or getattr(item, "title", str(item))))
                course = escape(str(getattr(item, "course_name", None) or getattr(item, "course_id", None) or getattr(item, "course", "Course")))
                due = escape(str(getattr(item, "due_at", None) or getattr(item, "due_date", "N/A")))
                items_html += f"""
                <tr style="border-bottom: 1px solid #fee2e2;">
                    <td style="padding: 10px 0; color: #991b1b; font-weight: 600;">{course}</td>
                    <td style="padding: 10px 0; color: #1e293b;">{title}</td>
                    <td style="padding: 10px 0; color: #64748b; font-size: 13px; text-align: right;">{due}</td>
                </tr>
                """
            
            html_sections.append(f"""
            <div style="margin-bottom: 24px; background: #fef2f2; border: 1px solid #fecaca; border-left: 5px solid #ef4444; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #991b1b; font-size: 16px; font-weight: 700; display: flex; align-items: center;">
                    <span style="background: #ef4444; color: #ffffff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px;">P0 ALERT</span>
                    Confirmed Missing Work ({len(missing_work)})
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    {items_html}
                </table>
            </div>
            """)

        if grade_drops:
            items_html = ""
            for item in grade_drops:
                course = escape(str(getattr(item, "course_name", None) or getattr(item, "course", "Course")))
                previous = escape(str(getattr(item, "previous_score", None) if getattr(item, "previous_score", None) is not None else (getattr(item, "prev_percentage", None) if getattr(item, "prev_percentage", None) is not None else getattr(item, "previous_grade", "N/A"))))
                current = escape(str(getattr(item, "current_score", None) if getattr(item, "current_score", None) is not None else (getattr(item, "curr_percentage", None) if getattr(item, "curr_percentage", None) is not None else getattr(item, "current_grade", "N/A"))))
                items_html += f"""
                <tr style="border-bottom: 1px solid #ffedd5;">
                    <td style="padding: 10px 0; color: #9a3412; font-weight: 600;">{course}</td>
                    <td style="padding: 10px 0; color: #1e293b;">Grade velocity drop</td>
                    <td style="padding: 10px 0; color: #c2410c; font-weight: 700; text-align: right;">{previous}% &rarr; {current}%</td>
                </tr>
                """

            html_sections.append(f"""
            <div style="margin-bottom: 24px; background: #fff7ed; border: 1px solid #fed7aa; border-left: 5px solid #f97316; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #9a3412; font-size: 16px; font-weight: 700; display: flex; align-items: center;">
                    <span style="background: #f97316; color: #ffffff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px;">P0 ALERT</span>
                    Grade Velocity Drops ({len(grade_drops)})
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    {items_html}
                </table>
            </div>
            """)

        if attendance_anomalies:
            items_html = ""
            for item in attendance_anomalies:
                course = escape(str(getattr(item, "course_name", None) or getattr(item, "course", "")))
                code = escape(str(getattr(item, "code", "UNEXCUSED")))
                date = escape(str(getattr(item, "date", "Today")))
                period = escape(str(getattr(item, "period", "N/A")))
                desc = escape(str(getattr(item, "description", "Unexcused Absence/Cut")))
                course_str = f" - {course}" if course else ""
                items_html += f"""
                <tr style="border-bottom: 1px solid #f3e8ff;">
                    <td style="padding: 10px 0; color: #6b21a8; font-weight: 600;">{date} (Per {period}){course_str}</td>
                    <td style="padding: 10px 0; color: #1e293b;">{desc}</td>
                    <td style="padding: 10px 0; text-align: right;"><span style="background: #a855f7; color: #ffffff; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 700;">{code}</span></td>
                </tr>
                """

            html_sections.append(f"""
            <div style="margin-bottom: 24px; background: #faf5ff; border: 1px solid #e9d5ff; border-left: 5px solid #a855f7; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #6b21a8; font-size: 16px; font-weight: 700; display: flex; align-items: center;">
                    <span style="background: #a855f7; color: #ffffff; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 8px;">P0 ALERT</span>
                    Attendance Anomalies ({len(attendance_anomalies)})
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    {items_html}
                </table>
            </div>
            """)

        sections_body = "\n".join(html_sections)

        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bellmon Academic Sentinel Alert</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8fafc; padding: 20px 0;">
        <tr>
            <td align="center">
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); margin: 20px auto;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 24px 32px; text-align: left;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">Bellmon Academic Sentinel</h1>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Daily Autonomous Telemetry Digest &amp; P0 Alert Dispatch</p>
                        </td>
                    </tr>
                    
                    <!-- Content Body -->
                    <tr>
                        <td style="padding: 32px;">
                            <h2 style="margin: 0 0 16px 0; color: #0f172a; font-size: 18px; font-weight: 600;">Urgent Academic Alert for <span style="color: #2563eb;">{escape(student_name)}</span></h2>
                            <p style="margin: 0 0 24px 0; color: #475569; font-size: 14px; line-height: 1.5;">
                                The Bellmon Academic Sentinel detected the following urgent P0 alert conditions during today's automated evaluation.
                            </p>
                            
                            {sections_body}
                            
                            <!-- Call to Action Footer -->
                            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0 0 12px 0; color: #64748b; font-size: 13px;">
                                    Please log into your school's LMS / SIS portal for details.
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 11px;">
                                    Sent autonomously by Bellmon Batch Orchestrator
                                </p>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_body, text_fallback

    def compile_heartbeat_email(self, payload: Any) -> Tuple[str, str]:
        """
        Compiles aggregated daily telemetry heartbeat payload into responsive HTML and plaintext email.

        Args:
            payload: HeartbeatPayload object or dict containing telemetry fields.

        Returns:
            Tuple of (html_body, text_fallback)
        """
        student_name = getattr(payload, "student_name", "Student")
        date_str = getattr(payload, "date", "")
        sync_ts = getattr(payload, "sync_timestamp", "") or date_str

        # Portal Statuses
        canvas_status = getattr(payload, "canvas_status", "OPERATIONAL")
        powerschool_status = getattr(payload, "powerschool_status", "OPERATIONAL")
        ingestion_list = getattr(payload, "ingestion_statuses", []) or []
        for rec in ingestion_list:
            pname = str(getattr(rec, "portal_name", "")).lower()
            pstat = str(getattr(rec, "status", "OPERATIONAL"))
            if "canvas" in pname:
                canvas_status = pstat
            elif "power" in pname:
                powerschool_status = pstat

        grace_watchlist = getattr(payload, "grace_watchlist", []) or []
        attendance_sum = getattr(payload, "attendance_summary", None)

        alerts_count = getattr(payload, "critical_alerts_dispatched_today", None)
        if alerts_count is None:
            alerts_count = getattr(payload, "alerts_dispatched_today", 0)

        zero_confirmed = getattr(payload, "zero_alert_confirmed", True) and (alerts_count == 0)

        # Build Plaintext Fallback
        text_lines = [
            "BELLMON ACADEMIC SENTINEL - DAILY HEARTBEAT & SYSTEM ACTIVITY BRIEFING",
            f"Student: {student_name}",
            f"Date: {date_str}",
            "=" * 50,
            "",
            "SYSTEM INGESTION HEALTH:",
            f"  - Canvas API: {canvas_status}",
            f"  - PowerSchool Portal: {powerschool_status}",
            "",
            "ACTIVE GRACE PERIOD WATCHLIST:",
        ]

        if grace_watchlist:
            for item in grace_watchlist:
                cname = getattr(item, "course_name", None) or getattr(item, "course_id", "Course")
                title = getattr(item, "title", "Assignment")
                due = getattr(item, "due_at", "N/A")
                hrs = getattr(item, "hours_remaining", 0.0)
                text_lines.append(f"  - [{cname}] {title} (Due: {due}, {hrs:.1f} hours remaining)")
        else:
            text_lines.append("  No active grace period items. All digital work submitted.")

        text_lines.append("")
        text_lines.append("DAILY ATTENDANCE TELEMETRY:")
        if attendance_sum:
            records = getattr(attendance_sum, "records", None) or getattr(attendance_sum, "periods", []) or []
            if records:
                for rec in records:
                    p = getattr(rec, "period", "?")
                    c = getattr(rec, "course_name", "Class")
                    st = getattr(rec, "status", None) or getattr(rec, "status_code", "P")
                    text_lines.append(f"  - Period {p} ({c}): {st}")
            else:
                text_lines.append("  All period check-ins normal.")
            anomalies = getattr(attendance_sum, "total_anomalies", 0)
            text_lines.append(f"  Total Anomalies: {anomalies}")
        else:
            text_lines.append("  No attendance data recorded for today.")

        text_lines.append("")
        text_lines.append("SENTINEL STANDING:")
        if zero_confirmed or alerts_count == 0:
            text_lines.append("  [OK] 0 Critical Alerts Dispatched Today")
        else:
            text_lines.append(f"  [!] {alerts_count} Critical Alert(s) Dispatched Today")

        text_lines.append("")
        text_lines.append("Sent autonomously by Bellmon Batch Orchestrator")
        text_fallback = "\n".join(text_lines)

        # Helper for status color badges
        def get_status_badge(status_str: str) -> str:
            st = status_str.upper()
            if st == "OPERATIONAL":
                return '<span style="background: #dcfce7; color: #166534; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700;">OPERATIONAL</span>'
            elif st == "DEGRADED":
                return '<span style="background: #fef9c3; color: #854d0e; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700;">DEGRADED</span>'
            else:
                return '<span style="background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700;">FAILED</span>'

        # Build HTML Sections
        canvas_badge = get_status_badge(canvas_status)
        ps_badge = get_status_badge(powerschool_status)

        # Ingestion Health Banner HTML
        ingestion_html = f"""
        <div style="margin-bottom: 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
            <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 15px; font-weight: 700;">
                System Ingestion Health
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 8px 0; color: #334155; font-weight: 600;">Canvas API</td>
                    <td style="padding: 8px 0; text-align: right;">{canvas_badge}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; color: #334155; font-weight: 600;">PowerSchool Portal</td>
                    <td style="padding: 8px 0; text-align: right;">{ps_badge}</td>
                </tr>
            </table>
        </div>
        """

        # Grace Watchlist HTML
        if grace_watchlist:
            items_rows = ""
            for item in grace_watchlist:
                cname = escape(str(getattr(item, "course_name", None) or getattr(item, "course_id", "Course")))
                title = escape(str(getattr(item, "title", "Assignment")))
                due = escape(str(getattr(item, "due_at", "N/A")))
                hrs = getattr(item, "hours_remaining", 0.0)
                items_rows += f"""
                <tr style="border-bottom: 1px solid #fef3c7;">
                    <td style="padding: 10px 0; color: #92400e; font-weight: 600;">{cname}</td>
                    <td style="padding: 10px 0; color: #1e293b;">{title}</td>
                    <td style="padding: 10px 0; color: #451a03; font-size: 13px;">{due}</td>
                    <td style="padding: 10px 0; color: #d97706; font-weight: 700; text-align: right;">{hrs:.1f} hours remaining</td>
                </tr>
                """
            watchlist_html = f"""
            <div style="margin-bottom: 24px; background: #fffbeb; border: 1px solid #fde68a; border-left: 5px solid #f59e0b; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #92400e; font-size: 15px; font-weight: 700;">
                    Grace Period Watchlist ({len(grace_watchlist)})
                </h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    {items_rows}
                </table>
            </div>
            """
        else:
            watchlist_html = """
            <div style="margin-bottom: 24px; background: #f0fdf4; border: 1px solid #bbf7d0; border-left: 5px solid #22c55e; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 4px 0; color: #166534; font-size: 15px; font-weight: 700;">Grace Period Watchlist</h3>
                <p style="margin: 0; color: #15803d; font-size: 14px;">No active grace period items. All digital work submitted.</p>
            </div>
            """

        # Daily Attendance HTML
        if attendance_sum:
            records = getattr(attendance_sum, "records", None) or getattr(attendance_sum, "periods", []) or []
            if records:
                att_rows = ""
                for rec in records:
                    p = escape(str(getattr(rec, "period", "?")))
                    c = escape(str(getattr(rec, "course_name", "Class")))
                    st = escape(str(getattr(rec, "status", None) or getattr(rec, "status_code", "P")))
                    att_rows += f"""
                    <tr style="border-bottom: 1px solid #f1f5f9;">
                        <td style="padding: 8px 0; color: #334155; font-weight: 600;">Period {p} ({c})</td>
                        <td style="padding: 8px 0; text-align: right; color: #0f172a; font-weight: 600;">{st}</td>
                    </tr>
                    """
                att_table = f'<table style="width: 100%; border-collapse: collapse; font-size: 14px;">{att_rows}</table>'
            else:
                att_table = '<p style="margin: 0; color: #475569; font-size: 14px;">All period check-ins normal.</p>'
            anomalies = getattr(attendance_sum, "total_anomalies", 0)
            anom_str = f'<div style="margin-top: 8px; font-size: 12px; color: #64748b;">Total Anomalies: {anomalies}</div>'
            attendance_html = f"""
            <div style="margin-bottom: 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 15px; font-weight: 700;">Daily Attendance Summary</h3>
                {att_table}
                {anom_str}
            </div>
            """
        else:
            attendance_html = """
            <div style="margin-bottom: 24px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 4px 0; color: #0f172a; font-size: 15px; font-weight: 700;">Daily Attendance Summary</h3>
                <p style="margin: 0; color: #64748b; font-size: 14px;">No attendance data recorded for today.</p>
            </div>
            """

        # Sentinel Standing HTML Badge
        if zero_confirmed or alerts_count == 0:
            standing_html = """
            <div style="margin-bottom: 24px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="background: #22c55e; color: #ffffff; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 700;">ZERO Critical Alerts Dispatched Today</span>
                <p style="margin: 8px 0 0 0; color: #166534; font-size: 13px;">Academic Sentinel Standing: CLEAR</p>
            </div>
            """
        else:
            standing_html = f"""
            <div style="margin-bottom: 24px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 16px; text-align: center;">
                <span style="background: #ef4444; color: #ffffff; padding: 4px 12px; border-radius: 9999px; font-size: 13px; font-weight: 700;">{alerts_count} Critical Alert(s) Dispatched Today</span>
                <p style="margin: 8px 0 0 0; color: #991b1b; font-size: 13px;">Academic Sentinel Standing: ACTION REQUIRED</p>
            </div>
            """

        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bellmon Daily Heartbeat Briefing</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8fafc; padding: 20px 0;">
        <tr>
            <td align="center">
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); margin: 20px auto;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 24px 32px; text-align: left;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">Bellmon Academic Sentinel</h1>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Daily System Activity &amp; Telemetry Briefing ({escape(date_str)})</p>
                        </td>
                    </tr>
                    
                    <!-- Content Body -->
                    <tr>
                        <td style="padding: 32px;">
                            <h2 style="margin: 0 0 16px 0; color: #0f172a; font-size: 18px; font-weight: 600;">Daily Briefing for <span style="color: #2563eb;">{escape(student_name)}</span></h2>
                            
                            {ingestion_html}
                            {watchlist_html}
                            {attendance_html}
                            {standing_html}
                            
                            <!-- Footer -->
                            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0; color: #94a3b8; font-size: 11px;">
                                    Sent autonomously by Bellmon Batch Orchestrator
                                </p>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_body, text_fallback

    def compile_homework_snapshot_email(self, payload: Any) -> Tuple[str, str]:
        """
        Renders responsive HTML email body and plaintext fallback for daily homework snapshot.

        Args:
            payload: HomeworkSnapshotPayload or object containing snapshot telemetry.

        Returns:
            Tuple of (html_body, text_fallback)
        """
        student_name = getattr(payload, "student_name", "Student")
        generated_at = getattr(payload, "generated_at", "")
        grace_items = getattr(payload, "grace_period_items", []) or []
        upcoming_items = getattr(payload, "upcoming_deadlines", []) or []
        completed_items = getattr(payload, "recently_completed", []) or []

        date_display = generated_at[:10] if generated_at else ""

        # --- Text Fallback ---
        text_lines = [
            f"BELLMON HOMEWORK SNAPSHOT - {student_name.upper()}",
            f"Generated: {generated_at}",
            "=" * 50,
        ]

        if grace_items:
            text_lines.append("\n!!! URGENT: PENDING GRACE PERIOD ITEMS !!!")
            for item in grace_items:
                title = getattr(item, "title", "Assignment")
                course = getattr(item, "course", "Course")
                due = getattr(item, "original_due_at", "")
                rem = getattr(item, "hours_remaining", 0.0)
                text_lines.append(f" - [GRACE PERIOD] {title} ({course}) | Due: {due} | Hours Left: {rem}h")

        text_lines.append(f"\nUPCOMING DEADLINES (NEXT 48 HOURS) [{len(upcoming_items)}]:")
        if not upcoming_items:
            text_lines.append(" - No upcoming deadlines within next 48 hours.")
        else:
            for item in upcoming_items:
                title = getattr(item, "title", "Assignment")
                course = getattr(item, "course", "Course")
                due = getattr(item, "due_at", "")
                sub = "Submitted" if getattr(item, "submitted", False) else "NOT SUBMITTED"
                text_lines.append(f" - {title} ({course}) | Due: {due} | Status: {sub}")

        text_lines.append(f"\nRECENTLY COMPLETED (PAST 24 HOURS) [{len(completed_items)}]:")
        if not completed_items:
            text_lines.append(" - No assignments completed in past 24 hours.")
        else:
            for item in completed_items:
                title = getattr(item, "title", "Assignment")
                course = getattr(item, "course", "Course")
                sub_at = getattr(item, "submitted_at", "")
                text_lines.append(f" - [COMPLETED] {title} ({course}) | Submitted At: {sub_at}")

        text_lines.append("\n" + "=" * 50)
        text_lines.append("Sent autonomously by Bellmon Batch Orchestrator")
        text_fallback = "\n".join(text_lines)

        # --- HTML Body Compilation ---
        # 1. Grace Period Red Alert Section
        grace_html = ""
        if grace_items:
            cards = ""
            for item in grace_items:
                title = escape(str(getattr(item, "title", "Assignment")))
                course = escape(str(getattr(item, "course", "Course")))
                due = escape(str(getattr(item, "original_due_at", "")))
                rem = escape(str(getattr(item, "hours_remaining", 0.0)))
                sub_url = getattr(item, "submission_url", None)
                url_btn = (
                    f'<a href="{escape(sub_url)}" style="display: inline-block; margin-top: 8px; background: #dc2626; color: #ffffff; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600;">Submit Assignment &rarr;</a>'
                    if sub_url
                    else ""
                )

                cards += f"""
                <div style="background: #ffffff; border-left: 4px solid #ef4444; border-radius: 6px; padding: 12px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 11px; font-weight: 700; color: #991b1b; text-transform: uppercase;">{course}</span>
                            <h4 style="margin: 2px 0 4px 0; font-size: 15px; color: #0f172a;">{title}</h4>
                            <p style="margin: 0; font-size: 12px; color: #64748b;">Original Due Date: {due}</p>
                        </div>
                        <span style="background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 9999px;">{rem}h Left</span>
                    </div>
                    {url_btn}
                </div>
                """
            grace_html = f"""
            <div style="margin-bottom: 24px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 16px;">
                <h3 style="margin: 0 0 12px 0; color: #9f1239; font-size: 15px; font-weight: 700; display: flex; align-items: center;">
                    🚨 Pending Grace Period Action Required ({len(grace_items)})
                </h3>
                <p style="margin: 0 0 12px 0; color: #be123c; font-size: 13px;">
                    The following digital missing items are within their active grace period window. Immediate submission is required to prevent P0 escalation.
                </p>
                {cards}
            </div>
            """

        # 2. Upcoming Deadlines (Next 48 Hours)
        if not upcoming_items:
            upcoming_html = """
            <div style="margin-bottom: 24px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 16px; text-align: center;">
                <p style="margin: 0; color: #64748b; font-size: 13px;">No upcoming deadlines scheduled in the next 48 hours.</p>
            </div>
            """
        else:
            cards = ""
            for item in upcoming_items:
                title = escape(str(getattr(item, "title", "Assignment")))
                course = escape(str(getattr(item, "course", "Course")))
                due = escape(str(getattr(item, "due_at", "")))
                portal = escape(str(getattr(item, "portal", "Canvas")))
                submitted = getattr(item, "submitted", False)
                sub_badge = (
                    '<span style="background: #dcfce7; color: #15803d; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 9999px;">✓ Submitted</span>'
                    if submitted
                    else '<span style="background: #fff7ed; color: #c2410c; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 9999px;">Pending</span>'
                )

                cards += f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <span style="font-size: 11px; font-weight: 600; color: #2563eb; text-transform: uppercase;">{course} • {portal}</span>
                            <h4 style="margin: 2px 0 4px 0; font-size: 14px; color: #0f172a;">{title}</h4>
                            <p style="margin: 0; font-size: 12px; color: #64748b;">Due: {due}</p>
                        </div>
                        {sub_badge}
                    </div>
                </div>
                """
            upcoming_html = f"""
            <div style="margin-bottom: 24px;">
                <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px; font-weight: 600;">
                    📅 Due Tomorrow &amp; Next 48 Hours ({len(upcoming_items)})
                </h3>
                {cards}
            </div>
            """

        # 3. Recently Completed (Past 24 Hours)
        if not completed_items:
            completed_html = """
            <div style="margin-bottom: 24px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; padding: 16px; text-align: center;">
                <p style="margin: 0; color: #64748b; font-size: 13px;">No completed assignments recorded in the past 24 hours.</p>
            </div>
            """
        else:
            cards = ""
            for item in completed_items:
                title = escape(str(getattr(item, "title", "Assignment")))
                course = escape(str(getattr(item, "course", "Course")))
                sub_at = escape(str(getattr(item, "submitted_at", "")))

                cards += f"""
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                    <span style="font-size: 11px; font-weight: 600; color: #166534;">{course}</span>
                    <p style="margin: 2px 0 0 0; font-size: 13px; font-weight: 600; color: #14532d;">✓ {title}</p>
                    <span style="font-size: 11px; color: #15803d;">Submitted: {sub_at}</span>
                </div>
                """
            completed_html = f"""
            <div style="margin-bottom: 24px;">
                <h3 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px; font-weight: 600;">
                    🎉 Recently Completed Work (Past 24h) ({len(completed_items)})
                </h3>
                {cards}
            </div>
            """

        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bellmon Evening Homework &amp; Deadline Snapshot</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8fafc; padding: 20px 0;">
        <tr>
            <td align="center">
                <table role="presentation" style="width: 100%; max-width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); margin: 20px auto;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #0f172a; padding: 24px 32px; text-align: left;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">Bellmon Academic Sentinel</h1>
                            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">Daily Evening Homework &amp; Deadline Snapshot ({escape(date_display)})</p>
                        </td>
                    </tr>
                    
                    <!-- Content Body -->
                    <tr>
                        <td style="padding: 32px;">
                            <h2 style="margin: 0 0 20px 0; color: #0f172a; font-size: 18px; font-weight: 600;">Evening Briefing for <span style="color: #2563eb;">{escape(student_name)}</span></h2>
                            
                            {grace_html}
                            {upcoming_html}
                            {completed_html}
                            
                            <!-- Footer -->
                            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <p style="margin: 0; color: #94a3b8; font-size: 11px;">
                                    Sent autonomously by Bellmon Batch Orchestrator
                                </p>
                            </div>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        return html_body, text_fallback


