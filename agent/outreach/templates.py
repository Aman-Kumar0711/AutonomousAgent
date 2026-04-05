from jinja2 import Template

# ---------------------------------------------------------------------------
# Shared HTML wrapper
# ---------------------------------------------------------------------------

_EMAIL_WRAPPER = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ subject }}</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#f4f4f5;">
<tr><td align="center" style="padding:32px 16px;">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
<!-- Header accent -->
<tr><td style="height:4px;background-color:#2563eb;"></td></tr>
<tr><td style="padding:32px 40px;">
{{ body_html }}
</td></tr>
<!-- Signature -->
<tr><td style="padding:0 40px 32px 40px;border-top:1px solid #e5e7eb;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr><td style="padding-top:24px;">
<p style="margin:0 0 4px 0;font-size:15px;font-weight:600;color:#111827;">{{ sender_name }}</p>
<p style="margin:0 0 2px 0;font-size:13px;color:#6b7280;">Web Developer & Digital Solutions</p>
<p style="margin:0;font-size:13px;"><a href="mailto:{{ sender_email }}" style="color:#2563eb;text-decoration:none;">{{ sender_email }}</a></p>
</td></tr>
</table>
</td></tr>
<!-- Footer -->
<tr><td style="padding:16px 40px;background-color:#f9fafb;border-top:1px solid #e5e7eb;">
<p style="margin:0;font-size:11px;color:#9ca3af;line-height:1.5;">
You're receiving this because your business was found in a public directory.
If you'd prefer not to hear from me, simply reply with "unsubscribe" and I'll remove you immediately.
</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Subject line templates
# ---------------------------------------------------------------------------

SUBJECT_INITIAL = Template(
    "{{ business_name }} — I found {{ issue_count }} issue{{ 's' if issue_count != 1 else '' }} on your website"
)

SUBJECT_FOLLOWUP_1 = Template(
    "Quick follow-up: {{ business_name }}'s website audit"
)

SUBJECT_FOLLOWUP_2 = Template(
    "Last chance: free website audit for {{ business_name }}"
)

# ---------------------------------------------------------------------------
# Initial outreach
# ---------------------------------------------------------------------------

_INITIAL_BODY = """\
<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Hi{{ ' ' + contact_name if contact_name else '' }},
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I came across <strong>{{ business_name }}</strong>{% if business_city %} in {{ business_city }}{% endif %}{% if rating %} — congrats on the {{ rating }}-star rating{% if review_count %} across {{ review_count }} reviews{% endif %}{% endif %}! It's clear you're doing something right with your {{ domain_label }} business.
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I'm a web developer and I took a quick look at your website. I noticed a few things that might be costing you customers:
</p>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;">
{% for issue in top_issues %}
<tr>
<td style="padding:12px 16px;{% if not loop.last %}border-bottom:1px solid #f3f4f6;{% endif %}">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0">
<tr>
<td style="vertical-align:top;width:8px;padding-top:6px;">
<div style="width:8px;height:8px;border-radius:50%;background-color:{% if issue.impact == 'high' %}#ef4444{% elif issue.impact == 'medium' %}#f59e0b{% else %}#6b7280{% endif %};"></div>
</td>
<td style="padding-left:12px;">
<p style="margin:0 0 4px 0;font-size:14px;font-weight:600;color:#111827;">{{ issue.issue }}</p>
<p style="margin:0;font-size:13px;color:#6b7280;line-height:1.5;">{{ issue.business_impact }}</p>
</td>
</tr>
</table>
</td>
</tr>
{% endfor %}
</table>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Your website scored <strong>{{ overall_score }}/100</strong> in my audit. I've put together a detailed report with specific fixes you can check out here:
</p>

<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px 0;">
<tr><td style="background-color:#2563eb;border-radius:6px;padding:12px 28px;">
<a href="{{ portfolio_url }}" style="color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;display:inline-block;">View Your Free Audit Report &rarr;</a>
</td></tr>
</table>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I can fix all of these issues for you — I build custom solutions based on exactly what each business needs. No cookie-cutter packages, just the stuff that'll actually bring you more customers.
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Would you be open to a quick chat? Just reply to this email and we can figure out what makes sense for {{ business_name }}.
</p>

<p style="margin:0;font-size:15px;color:#374151;line-height:1.6;">
Either way, the audit report is yours to keep — no strings attached.
</p>

<p style="margin:16px 0 0 0;font-size:15px;color:#374151;line-height:1.6;">
Cheers,<br>{{ sender_name }}
</p>
"""

# ---------------------------------------------------------------------------
# Follow-up 1 (3 days)
# ---------------------------------------------------------------------------

_FOLLOWUP_1_BODY = """\
<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Hi{{ ' ' + contact_name if contact_name else '' }},
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I reached out a few days ago about some issues I found on the {{ business_name }} website. I know you're busy running your business, so I wanted to highlight one thing in particular:
</p>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:20px;background-color:#fef3c7;border-radius:8px;border-left:4px solid #f59e0b;">
<tr><td style="padding:16px 20px;">
<p style="margin:0 0 4px 0;font-size:14px;font-weight:600;color:#92400e;">{{ highlight_issue.issue }}</p>
<p style="margin:0;font-size:13px;color:#78350f;line-height:1.5;">{{ highlight_issue.business_impact }}</p>
</td></tr>
</table>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Your full audit report is still available here:
</p>

<table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px 0;">
<tr><td style="background-color:#2563eb;border-radius:6px;padding:12px 28px;">
<a href="{{ portfolio_url }}" style="color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;display:inline-block;">View Audit Report &rarr;</a>
</td></tr>
</table>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I can usually fix issues like this within a few days. Happy to chat about it if you're interested — just reply to this email.
</p>

<p style="margin:0;font-size:15px;color:#374151;line-height:1.6;">
Cheers,<br>{{ sender_name }}
</p>
"""

# ---------------------------------------------------------------------------
# Follow-up 2 (7 days)
# ---------------------------------------------------------------------------

_FOLLOWUP_2_BODY = """\
<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Hi{{ ' ' + contact_name if contact_name else '' }},
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Just a final note — I won't keep bugging you after this.
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
Your free website audit for <strong>{{ business_name }}</strong> is still live: <a href="{{ portfolio_url }}" style="color:#2563eb;text-decoration:none;font-weight:600;">view report</a>.
</p>

<p style="margin:0 0 16px 0;font-size:15px;color:#374151;line-height:1.6;">
I've helped multiple local businesses fix these exact issues and start getting more customers from their website. If you ever want to revisit the findings, just reply to this email — I'm always happy to help.
</p>

<p style="margin:0;font-size:15px;color:#374151;line-height:1.6;">
Wishing {{ business_name }} continued success!
</p>

<p style="margin:16px 0 0 0;font-size:15px;color:#374151;line-height:1.6;">
— {{ sender_name }}
</p>
"""

# ---------------------------------------------------------------------------
# Compiled Jinja2 templates
# ---------------------------------------------------------------------------

INITIAL_BODY_TEMPLATE = Template(_INITIAL_BODY)
FOLLOWUP_1_BODY_TEMPLATE = Template(_FOLLOWUP_1_BODY)
FOLLOWUP_2_BODY_TEMPLATE = Template(_FOLLOWUP_2_BODY)
EMAIL_WRAPPER_TEMPLATE = Template(_EMAIL_WRAPPER)


# ---------------------------------------------------------------------------
# Public rendering helpers
# ---------------------------------------------------------------------------

DOMAIN_LABELS = {
    "restaurant": "restaurant",
    "healthcare": "healthcare",
    "dental": "dental",
    "retail": "retail",
    "real_estate": "real estate",
    "legal": "legal",
    "automotive": "automotive",
    "beauty": "beauty & wellness",
    "fitness": "fitness",
    "education": "education",
    "professional_services": "professional services",
    "home_services": "home services",
    "other": "local",
}


def render_initial_outreach(
    *,
    business_name: str,
    contact_name: str | None,
    business_city: str | None,
    domain: str | None,
    rating: float | None,
    review_count: int | None,
    top_issues: list[dict],
    overall_score: int,
    portfolio_url: str,
    sender_name: str,
    sender_email: str,
) -> tuple[str, str]:
    domain_label = DOMAIN_LABELS.get(domain or "other", "local")
    subject = SUBJECT_INITIAL.render(
        business_name=business_name,
        issue_count=len(top_issues),
    )
    body_html = INITIAL_BODY_TEMPLATE.render(
        contact_name=contact_name,
        business_name=business_name,
        business_city=business_city,
        domain_label=domain_label,
        rating=rating,
        review_count=review_count,
        top_issues=top_issues[:3],
        overall_score=overall_score,
        portfolio_url=portfolio_url,
        sender_name=sender_name,
    )
    html = EMAIL_WRAPPER_TEMPLATE.render(
        subject=subject,
        body_html=body_html,
        sender_name=sender_name,
        sender_email=sender_email,
    )
    return subject, html


def render_follow_up_1(
    *,
    business_name: str,
    contact_name: str | None,
    highlight_issue: dict,
    portfolio_url: str,
    sender_name: str,
    sender_email: str,
) -> tuple[str, str]:
    subject = SUBJECT_FOLLOWUP_1.render(business_name=business_name)
    body_html = FOLLOWUP_1_BODY_TEMPLATE.render(
        contact_name=contact_name,
        business_name=business_name,
        highlight_issue=highlight_issue,
        portfolio_url=portfolio_url,
        sender_name=sender_name,
    )
    html = EMAIL_WRAPPER_TEMPLATE.render(
        subject=subject,
        body_html=body_html,
        sender_name=sender_name,
        sender_email=sender_email,
    )
    return subject, html


def render_follow_up_2(
    *,
    business_name: str,
    contact_name: str | None,
    portfolio_url: str,
    sender_name: str,
    sender_email: str,
) -> tuple[str, str]:
    subject = SUBJECT_FOLLOWUP_2.render(business_name=business_name)
    body_html = FOLLOWUP_2_BODY_TEMPLATE.render(
        contact_name=contact_name,
        business_name=business_name,
        portfolio_url=portfolio_url,
        sender_name=sender_name,
    )
    html = EMAIL_WRAPPER_TEMPLATE.render(
        subject=subject,
        body_html=body_html,
        sender_name=sender_name,
        sender_email=sender_email,
    )
    return subject, html
