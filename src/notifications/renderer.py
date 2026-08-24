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
