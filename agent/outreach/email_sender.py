import smtplib
import time
from collections import deque
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from rich.console import Console

from ..config import (
    FROM_EMAIL,
    FROM_NAME,
    RESEND_API_KEY,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
    YOUR_EMAIL,
    YOUR_NAME,
)
from ..database.models import Business, OutreachRecord, WebsiteAudit
from .templates import render_follow_up_1, render_follow_up_2, render_initial_outreach

console = Console()

MAX_EMAILS_PER_HOUR = 80


class EmailSender:
    def __init__(self):
        self._send_timestamps: deque[float] = deque()

        self.use_resend = bool(RESEND_API_KEY) and not SMTP_USER
        if self.use_resend:
            try:
                import resend as _resend

                _resend.api_key = RESEND_API_KEY
                self._resend = _resend
            except ImportError:
                console.print(
                    "[yellow]resend package not installed, falling back to SMTP[/yellow]"
                )
                self.use_resend = False

    # ----------------------------------------------------------------- public

    def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        self._rate_limit()

        if self.use_resend:
            return self._send_via_resend(to, subject, html_body)
        return self._send_via_smtp(to, subject, html_body, text_body)

    def send_outreach(
        self,
        business: Business,
        audit: WebsiteAudit,
        portfolio_url: str,
    ) -> bool:
        if not business.email:
            console.print(
                f"[yellow]Skipping {business.name}: no email[/yellow]"
            )
            return False

        issues = audit.issues or []
        high_issues = [i for i in issues if i.get("impact") == "high"]
        top_issues = (high_issues or issues)[:3]

        subject, html = render_initial_outreach(
            business_name=business.name,
            contact_name=None,
            business_city=business.city,
            domain=business.domain,
            rating=business.rating,
            review_count=business.review_count,
            top_issues=top_issues,
            overall_score=audit.overall_score or 0,
            portfolio_url=portfolio_url,
            sender_name=YOUR_NAME,
            sender_email=YOUR_EMAIL,
        )

        console.print(
            f"  [cyan]Sending to {business.name}[/cyan] <{business.email}>"
        )
        return self.send_email(business.email, subject, html)

    def send_follow_up(
        self,
        business: Business,
        outreach: OutreachRecord,
    ) -> bool:
        if not business.email:
            return False

        portfolio_url = outreach.portfolio_url or ""
        follow_up_num = outreach.follow_up_count + 1

        if follow_up_num == 1:
            issues = []
            for audit_record in business.audits:
                if audit_record.issues:
                    issues = audit_record.issues
                    break

            highlight = issues[0] if issues else {
                "issue": "Website needs improvement",
                "business_impact": "Your website may be losing potential customers.",
            }

            subject, html = render_follow_up_1(
                business_name=business.name,
                contact_name=None,
                highlight_issue=highlight,
                portfolio_url=portfolio_url,
                sender_name=YOUR_NAME,
                sender_email=YOUR_EMAIL,
            )
        else:
            subject, html = render_follow_up_2(
                business_name=business.name,
                contact_name=None,
                portfolio_url=portfolio_url,
                sender_name=YOUR_NAME,
                sender_email=YOUR_EMAIL,
            )

        console.print(
            f"  [cyan]Follow-up #{follow_up_num} to {business.name}[/cyan]"
        )
        return self.send_email(business.email, subject, html)

    # ---------------------------------------------------------------- private

    def _rate_limit(self) -> None:
        now = time.time()
        while self._send_timestamps and now - self._send_timestamps[0] > 3600:
            self._send_timestamps.popleft()

        if len(self._send_timestamps) >= MAX_EMAILS_PER_HOUR:
            wait = 3600 - (now - self._send_timestamps[0])
            console.print(
                f"[yellow]Rate limit reached. Waiting {wait:.0f}s...[/yellow]"
            )
            time.sleep(wait + 1)

        self._send_timestamps.append(time.time())

    def _send_via_smtp(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        if not SMTP_USER or not SMTP_PASSWORD:
            console.print("[red]SMTP credentials not configured. Set SMTP_PASSWORD in .env[/red]")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{FROM_NAME or YOUR_NAME} <{FROM_EMAIL or SMTP_USER}>"
            msg["To"] = to
            msg["Subject"] = subject

            if text_body:
                msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            console.print(f"    [green]Email sent to {to}[/green]")
            return True

        except Exception as e:
            console.print(f"    [red]SMTP error: {e}[/red]")
            return False

    def _send_via_resend(
        self,
        to: str,
        subject: str,
        html_body: str,
    ) -> bool:
        try:
            params = {
                "from": f"{FROM_NAME or YOUR_NAME} <{FROM_EMAIL}>",
                "to": [to],
                "subject": subject,
                "html": html_body,
            }
            self._resend.Emails.send(params)
            console.print(f"    [green]Email sent via Resend to {to}[/green]")
            return True

        except Exception as e:
            console.print(f"    [red]Resend error: {e}[/red]")
            return False
