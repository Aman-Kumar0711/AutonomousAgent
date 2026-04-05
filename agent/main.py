import sys
from datetime import datetime, timezone

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

from .config import EXPORT_DIR, SERPAPI_KEY
from .database.db import DatabaseManager
from .outreach.email_sender import EmailSender
from .scraper.google_maps import GoogleMapsScraper
from .scraper.google_search import GoogleSearchScraper
from .scraper.website_analyzer import WebsiteAnalyzer
from .utils.helpers import generate_portfolio_url

console = Console()
db = DatabaseManager()


@click.group()
def cli():
    """Autonomous Lead Generation Agent"""
    pass


# --------------------------------------------------------------------------
# scrape
# --------------------------------------------------------------------------

@cli.command()
@click.option("--type", "business_type", required=True, help="Business type (e.g. restaurants, dentists, salons)")
@click.option("--city", required=True, help="City name (e.g. 'Los Angeles', 'Amsterdam', 'Toronto')")
@click.option("--state", default="", help="State/province (e.g. CA, TX, ON) — optional for non-US")
@click.option("--country", default="us", help="Country code: us, ca, uk, nl, de, fr, au, in, ae, sg")
@click.option("--limit", default=20, help="Max results to fetch")
def scrape(business_type: str, city: str, state: str, country: str, limit: int):
    """Scrape Google Maps for businesses worldwide."""
    if not SERPAPI_KEY:
        console.print("[red]Set SERPAPI_KEY in your .env file first.[/red]")
        sys.exit(1)

    location = f"{city}, {state}" if state else city
    console.print(Panel(
        f"[bold]Scraping {business_type} in {location} ({country.upper()})[/bold]\nLimit: {limit}",
        title="Lead Scraper",
        border_style="cyan",
    ))

    maps_scraper = GoogleMapsScraper()
    search_scraper = GoogleSearchScraper()

    results = maps_scraper.search_businesses(business_type, city, state, country)
    results = results[:limit]

    saved = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Saving & enriching...", total=len(results))

        for biz_data in results:
            enriched = search_scraper.enrich_business(biz_data)
            db.add_business(enriched)
            saved += 1
            progress.advance(task)

    console.print(f"\n[bold green]Saved {saved} businesses to database.[/bold green]")


# --------------------------------------------------------------------------
# audit
# --------------------------------------------------------------------------

@cli.command()
@click.option("--all", "audit_all", is_flag=True, help="Audit all un-audited businesses")
@click.option("--id", "business_id", type=int, help="Audit a specific business by ID")
def audit(audit_all: bool, business_id: int | None):
    """Audit business websites for issues."""
    analyzer = WebsiteAnalyzer()

    if business_id:
        businesses = []
        biz = db.get_business(business_id)
        if biz:
            businesses.append(biz)
        else:
            console.print(f"[red]Business #{business_id} not found.[/red]")
            return
    elif audit_all:
        businesses = db.get_businesses_without_audit()
    else:
        console.print("[yellow]Specify --all or --id <ID>[/yellow]")
        return

    if not businesses:
        console.print("[yellow]No businesses to audit.[/yellow]")
        return

    console.print(Panel(
        f"[bold]Auditing {len(businesses)} website(s)[/bold]",
        title="Website Auditor",
        border_style="cyan",
    ))

    for biz in businesses:
        if not biz.website:
            console.print(f"  [dim]Skipping {biz.name}: no website[/dim]")
            continue

        try:
            audit_data = analyzer.analyze(biz.website)
            db.add_audit(biz.id, audit_data)
            score = audit_data.get("overall_score", 0)
            issue_count = len(audit_data.get("issues", []))
            color = "green" if score >= 70 else "yellow" if score >= 40 else "red"
            console.print(
                f"  [{color}]{biz.name}: {score}/100 ({issue_count} issues)[/{color}]"
            )
        except Exception as e:
            console.print(f"  [red]Error auditing {biz.name}: {e}[/red]")

    console.print("\n[bold green]Audit complete.[/bold green]")


# --------------------------------------------------------------------------
# outreach
# --------------------------------------------------------------------------

@cli.command()
@click.option("--all", "send_all", is_flag=True, help="Send to all eligible businesses")
@click.option("--id", "business_id", type=int, help="Send to a specific business")
@click.option("--dry-run", is_flag=True, help="Preview without sending")
def outreach(send_all: bool, business_id: int | None, dry_run: bool):
    """Send outreach emails to businesses."""
    sender = EmailSender()

    if business_id:
        businesses = []
        biz = db.get_business(business_id)
        if biz:
            businesses.append(biz)
        else:
            console.print(f"[red]Business #{business_id} not found.[/red]")
            return
    elif send_all:
        businesses = db.get_businesses_without_outreach()
    else:
        console.print("[yellow]Specify --all or --id <ID>[/yellow]")
        return

    if not businesses:
        console.print("[yellow]No businesses ready for outreach.[/yellow]")
        return

    console.print(Panel(
        f"[bold]Outreach to {len(businesses)} business(es)[/bold]"
        + (" [yellow](DRY RUN)[/yellow]" if dry_run else ""),
        title="Email Outreach",
        border_style="cyan",
    ))

    if not dry_run:
        if not click.confirm(f"Send emails to {len(businesses)} businesses?"):
            console.print("[dim]Cancelled.[/dim]")
            return

    sent = 0
    for biz in businesses:
        audit_record = db.get_audit(biz.id)
        if not audit_record:
            console.print(f"  [dim]Skipping {biz.name}: no audit[/dim]")
            continue

        portfolio_url = generate_portfolio_url(biz.id, biz.name)

        if dry_run:
            console.print(f"  [cyan]Would send to:[/cyan] {biz.name} <{biz.email}>")
            console.print(f"    Score: {audit_record.overall_score}/100 | Issues: {len(audit_record.issues or [])}")
            continue

        success = sender.send_outreach(biz, audit_record, portfolio_url)
        if success:
            outreach_data = {
                "email_sent": True,
                "email_sent_at": datetime.now(timezone.utc),
                "email_subject": f"{biz.name} — website audit",
                "email_body_preview": f"Found issues on {biz.website}",
                "template_used": "initial_outreach",
                "status": "sent",
                "portfolio_url": portfolio_url,
            }
            db.add_outreach(biz.id, outreach_data)
            sent += 1

    console.print(f"\n[bold green]{'Would send' if dry_run else 'Sent'} {sent if not dry_run else len(businesses)} emails.[/bold green]")


# --------------------------------------------------------------------------
# follow-up
# --------------------------------------------------------------------------

@cli.command("follow-up")
def follow_up():
    """Send follow-up emails."""
    sender = EmailSender()
    businesses = db.get_all_businesses(status="contacted")

    eligible = []
    for biz in businesses:
        with db.get_session() as session:
            from .database.models import OutreachRecord
            outreach = (
                session.query(OutreachRecord)
                .filter(OutreachRecord.business_id == biz.id)
                .order_by(OutreachRecord.created_at.desc())
                .first()
            )
            if outreach and outreach.follow_up_count < 2:
                session.expunge(outreach)
                eligible.append((biz, outreach))

    if not eligible:
        console.print("[yellow]No businesses eligible for follow-up.[/yellow]")
        return

    console.print(Panel(
        f"[bold]Following up with {len(eligible)} business(es)[/bold]",
        title="Follow-Up",
        border_style="cyan",
    ))

    for biz, outreach in eligible:
        success = sender.send_follow_up(biz, outreach)
        if success:
            db.update_outreach_status(outreach.id, "followed_up")

    console.print("[bold green]Follow-ups complete.[/bold green]")


# --------------------------------------------------------------------------
# export
# --------------------------------------------------------------------------

@cli.command()
def export():
    """Export data to JSON for the dashboard."""
    console.print(Panel(
        f"[bold]Exporting to {EXPORT_DIR}[/bold]",
        title="Data Export",
        border_style="cyan",
    ))
    db.export_to_json()
    console.print("[bold green]Export complete.[/bold green]")


# --------------------------------------------------------------------------
# stats
# --------------------------------------------------------------------------

@cli.command()
def stats():
    """Show database statistics."""
    data = db.get_stats()

    table = Table(title="Lead Generation Stats", border_style="cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Businesses", str(data["total_businesses"]))
    table.add_row("Audited", str(data["total_audited"]))
    table.add_row("Contacted", str(data["total_contacted"]))
    table.add_row("Avg. Audit Score", str(data["average_audit_score"]))

    console.print(table)

    if data["by_status"]:
        status_table = Table(title="By Status", border_style="blue")
        status_table.add_column("Status")
        status_table.add_column("Count", justify="right")
        for status, count in data["by_status"].items():
            status_table.add_row(status, str(count))
        console.print(status_table)

    if data["by_domain"]:
        domain_table = Table(title="By Domain/Industry", border_style="green")
        domain_table.add_column("Domain")
        domain_table.add_column("Count", justify="right")
        for domain, count in sorted(data["by_domain"].items(), key=lambda x: x[1], reverse=True):
            domain_table.add_row(domain, str(count))
        console.print(domain_table)


# --------------------------------------------------------------------------
# run (full pipeline)
# --------------------------------------------------------------------------

@cli.command()
@click.option("--type", "business_type", required=True, help="Business type")
@click.option("--city", required=True, help="City name")
@click.option("--state", default="", help="State/province — optional for non-US")
@click.option("--country", default="us", help="Country code: us, ca, uk, nl, de, fr, au")
@click.option("--limit", default=20, help="Max results")
def run(business_type: str, city: str, state: str, country: str, limit: int):
    """Run the full pipeline: scrape → audit → export → outreach."""
    if not SERPAPI_KEY:
        console.print("[red]Set SERPAPI_KEY in your .env file first.[/red]")
        sys.exit(1)

    location = f"{city}, {state}" if state else city
    console.print(Panel(
        f"[bold]Full Pipeline[/bold]\n"
        f"Type: {business_type} | Location: {location} ({country.upper()}) | Limit: {limit}",
        title="Autonomous Agent",
        border_style="bold cyan",
    ))

    # Step 1: Scrape
    console.print("\n[bold cyan]Step 1/4: Scraping[/bold cyan]")
    maps_scraper = GoogleMapsScraper()
    search_scraper = GoogleSearchScraper()

    results = maps_scraper.search_businesses(business_type, city, state, country)
    results = results[:limit]

    saved = 0
    for biz_data in results:
        enriched = search_scraper.enrich_business(biz_data)
        db.add_business(enriched)
        saved += 1

    console.print(f"  [green]Saved {saved} businesses[/green]")

    # Step 2: Audit
    console.print("\n[bold cyan]Step 2/4: Auditing websites[/bold cyan]")
    analyzer = WebsiteAnalyzer()
    to_audit = db.get_businesses_without_audit()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Auditing...", total=len(to_audit))
        for biz in to_audit:
            if biz.website:
                try:
                    audit_data = analyzer.analyze(biz.website)
                    db.add_audit(biz.id, audit_data)
                except Exception as e:
                    console.print(f"  [red]Error: {biz.name}: {e}[/red]")
            progress.advance(task)

    # Step 3: Export
    console.print("\n[bold cyan]Step 3/4: Exporting data[/bold cyan]")
    db.export_to_json()
    console.print("  [green]Data exported for dashboard[/green]")

    # Step 4: Outreach
    console.print("\n[bold cyan]Step 4/4: Outreach[/bold cyan]")
    eligible = db.get_businesses_without_outreach()
    if eligible:
        console.print(f"  [yellow]{len(eligible)} businesses ready for outreach.[/yellow]")
        if click.confirm("  Send outreach emails now?"):
            sender = EmailSender()
            sent = 0
            for biz in eligible:
                audit_record = db.get_audit(biz.id)
                if not audit_record:
                    continue
                portfolio_url = generate_portfolio_url(biz.id, biz.name)
                success = sender.send_outreach(biz, audit_record, portfolio_url)
                if success:
                    outreach_data = {
                        "email_sent": True,
                        "email_sent_at": datetime.now(timezone.utc),
                        "email_subject": f"{biz.name} — website audit",
                        "email_body_preview": f"Found issues on {biz.website}",
                        "template_used": "initial_outreach",
                        "status": "sent",
                        "portfolio_url": portfolio_url,
                    }
                    db.add_outreach(biz.id, outreach_data)
                    sent += 1
            console.print(f"  [green]Sent {sent} emails[/green]")
        else:
            console.print("  [dim]Skipped outreach.[/dim]")
    else:
        console.print("  [dim]No businesses eligible for outreach.[/dim]")

    # Summary
    console.print()
    data = db.get_stats()
    console.print(Panel(
        f"[bold green]Pipeline Complete[/bold green]\n"
        f"Businesses: {data['total_businesses']} | "
        f"Audited: {data['total_audited']} | "
        f"Contacted: {data['total_contacted']} | "
        f"Avg Score: {data['average_audit_score']}",
        border_style="green",
    ))


# --------------------------------------------------------------------------
# manual (no SerpAPI needed — paste website directly)
# --------------------------------------------------------------------------

@cli.command()
@click.option("--website", required=True, help="Business website URL")
@click.option("--email", default="", help="Business email (auto-detected if not provided)")
@click.option("--name", default="", help="Business name (extracted from site if not provided)")
@click.option("--domain", default="other", help="Industry: restaurant, dental, retail, beauty, etc.")
@click.option("--send", is_flag=True, help="Send outreach email after audit")
def manual(website: str, email: str, name: str, domain: str, send: bool):
    """Add a business manually — no SerpAPI needed. Just paste a website URL."""
    from .scraper.google_search import GoogleSearchScraper
    from .utils.helpers import extract_domain

    console.print(Panel(
        f"[bold]Manual Mode[/bold]\nWebsite: {website}",
        title="Manual Entry",
        border_style="cyan",
    ))

    if not website.startswith(("http://", "https://")):
        website = f"https://{website}"

    # Auto-detect name from domain if not provided
    if not name:
        site_domain = extract_domain(website)
        name = site_domain.split(".")[0].title() if site_domain else "Unknown Business"

    # Auto-find email if not provided
    if not email:
        console.print("  [dim]Searching for email...[/dim]")
        search_scraper = GoogleSearchScraper()
        emails = search_scraper.find_business_emails(website)
        if emails:
            email = emails[0]
            console.print(f"  [green]Found email: {email}[/green]")
        else:
            console.print("  [yellow]No email found. Provide with --email flag to send outreach.[/yellow]")

    # Save to database
    biz_data = {
        "name": name,
        "website": website,
        "email": email or None,
        "domain": domain,
        "source": "manual",
    }
    biz = db.add_business(biz_data)
    console.print(f"  [green]Saved: {name} (ID: {biz.id})[/green]")

    # Audit the website
    console.print("\n[bold cyan]Auditing website...[/bold cyan]")
    analyzer = WebsiteAnalyzer()
    try:
        audit_data = analyzer.analyze(website)
        db.add_audit(biz.id, audit_data)
        score = audit_data.get("overall_score", 0)
        issue_count = len(audit_data.get("issues", []))
        color = "green" if score >= 70 else "yellow" if score >= 40 else "red"
        console.print(f"  [{color}]Score: {score}/100 | Issues: {issue_count}[/{color}]")

        # Show top issues
        for issue in audit_data.get("issues", [])[:5]:
            impact_color = {"high": "red", "medium": "yellow", "low": "dim"}.get(issue["impact"], "dim")
            console.print(f"    [{impact_color}]• {issue['issue']}[/{impact_color}]")

    except Exception as e:
        console.print(f"  [red]Audit error: {e}[/red]")
        return

    # Export
    db.export_to_json()
    console.print("  [green]Data exported for dashboard[/green]")

    # Send outreach if requested
    if send and email:
        console.print("\n[bold cyan]Sending outreach email...[/bold cyan]")
        audit_record = db.get_audit(biz.id)
        if audit_record:
            portfolio_url = generate_portfolio_url(biz.id, name)
            sender = EmailSender()
            success = sender.send_outreach(biz, audit_record, portfolio_url)
            if success:
                outreach_data = {
                    "email_sent": True,
                    "email_sent_at": datetime.now(timezone.utc),
                    "email_subject": f"{name} — website audit",
                    "email_body_preview": f"Found issues on {website}",
                    "template_used": "initial_outreach",
                    "status": "sent",
                    "portfolio_url": portfolio_url,
                }
                db.add_outreach(biz.id, outreach_data)
    elif send and not email:
        console.print("  [yellow]Cannot send: no email address. Use --email flag.[/yellow]")

    console.print(Panel(
        f"[bold green]Done![/bold green]\n"
        f"{name} | Score: {audit_data.get('overall_score', 0)}/100 | "
        f"Issues: {len(audit_data.get('issues', []))}",
        border_style="green",
    ))


# --------------------------------------------------------------------------
# batch (process multiple websites from a file)
# --------------------------------------------------------------------------

@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--send", is_flag=True, help="Send outreach emails after audit")
def batch(filepath: str, send: bool):
    """Process multiple websites from a text file. One URL per line.

    File format (one per line): website | email (optional) | name (optional)

    Example file:
      https://joespizza.com | joe@joespizza.com | Joe's Pizza
      https://bestdental.com
      https://salon123.com | info@salon123.com
    """
    from .scraper.google_search import GoogleSearchScraper
    from .utils.helpers import extract_domain

    with open(filepath) as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    console.print(Panel(
        f"[bold]Batch Mode[/bold]\nProcessing {len(lines)} websites from {filepath}",
        title="Batch Entry",
        border_style="cyan",
    ))

    search_scraper = GoogleSearchScraper()
    analyzer = WebsiteAnalyzer()
    processed = 0

    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        website = parts[0]
        email = parts[1] if len(parts) > 1 else ""
        name = parts[2] if len(parts) > 2 else ""

        if not website.startswith(("http://", "https://")):
            website = f"https://{website}"

        if not name:
            site_domain = extract_domain(website)
            name = site_domain.split(".")[0].title() if site_domain else "Unknown"

        if not email:
            emails = search_scraper.find_business_emails(website)
            if emails:
                email = emails[0]

        biz_data = {
            "name": name,
            "website": website,
            "email": email or None,
            "source": "manual",
        }
        biz = db.add_business(biz_data)

        try:
            audit_data = analyzer.analyze(website)
            db.add_audit(biz.id, audit_data)
            score = audit_data.get("overall_score", 0)
            color = "green" if score >= 70 else "yellow" if score >= 40 else "red"
            console.print(f"  [{color}]{name}: {score}/100[/{color}]")

            if send and email:
                audit_record = db.get_audit(biz.id)
                if audit_record:
                    portfolio_url = generate_portfolio_url(biz.id, name)
                    sender = EmailSender()
                    sender.send_outreach(biz, audit_record, portfolio_url)
                    db.add_outreach(biz.id, {
                        "email_sent": True,
                        "email_sent_at": datetime.now(timezone.utc),
                        "email_subject": f"{name} — website audit",
                        "template_used": "initial_outreach",
                        "status": "sent",
                        "portfolio_url": portfolio_url,
                    })

            processed += 1
        except Exception as e:
            console.print(f"  [red]Error: {name}: {e}[/red]")

    db.export_to_json()
    console.print(f"\n[bold green]Processed {processed}/{len(lines)} websites.[/bold green]")


def main():
    cli()


if __name__ == "__main__":
    main()
