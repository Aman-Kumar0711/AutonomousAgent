import re
import time

import requests
from bs4 import BeautifulSoup
from rich.console import Console
from serpapi import GoogleSearch

from ..config import MAX_RESULTS_PER_QUERY, SCRAPE_DELAY, SERPAPI_KEY
from ..utils.helpers import categorize_business, clean_email, clean_phone, extract_domain

console = Console()

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)
PHONE_REGEX = re.compile(
    r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

CONTACT_PAGE_PATHS = [
    "/contact", "/contact-us", "/about", "/about-us",
    "/team", "/our-team", "/get-in-touch",
]

BLACKLISTED_EMAIL_DOMAINS = {
    "example.com", "sentry.io", "wixpress.com", "googleapis.com",
    "w3.org", "schema.org", "facebook.com", "twitter.com",
    "google.com", "cloudflare.com", "wordpress.org", "tambourine.com",
    "ingest.sentry.io", "ingest.us.sentry.io", "squarespace.com",
    "wix.com", "godaddy.com", "shopify.com", "mailchimp.com",
    "hubspot.com", "typeform.com", "jotform.com", "formspree.io",
    "netlify.com", "vercel.com", "herokuapp.com", "github.com",
    "jquery.com", "jsdelivr.net", "cdnjs.com", "googleusercontent.com",
    "gstatic.com", "bootstrapcdn.com", "fontawesome.com",
}


class GoogleSearchScraper:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or SERPAPI_KEY
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def search_for_businesses(
        self, query: str, num_results: int = 20
    ) -> list[dict]:
        results: list[dict] = []
        collected = 0
        start = 0

        console.print(f"[cyan]Searching Google:[/cyan] {query}")

        while collected < num_results:
            try:
                params = {
                    "engine": "google",
                    "q": query,
                    "api_key": self.api_key,
                    "start": start,
                    "num": min(10, num_results - collected),
                }
                search = GoogleSearch(params)
                data = search.get_dict()

                organic = data.get("organic_results", [])
                if not organic:
                    break

                for item in organic:
                    if collected >= num_results:
                        break

                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")

                    if not link or any(
                        s in link
                        for s in [
                            "yelp.com", "facebook.com", "instagram.com",
                            "twitter.com", "linkedin.com", "wikipedia.org",
                            "tripadvisor.com", "yellowpages.com",
                        ]
                    ):
                        continue

                    business = {
                        "name": title,
                        "website": link,
                        "source": "google_search",
                    }
                    results.append(business)
                    collected += 1

                start += len(organic)
                time.sleep(SCRAPE_DELAY)

            except Exception as e:
                console.print(f"[red]Google Search error: {e}[/red]")
                break

        console.print(
            f"[bold green]Found {len(results)} results for '{query}'[/bold green]"
        )
        return results

    def find_business_emails(self, website_url: str) -> list[str]:
        emails: set[str] = set()
        site_domain = extract_domain(website_url)

        urls_to_check = [website_url]
        base = website_url.rstrip("/")
        for path in CONTACT_PAGE_PATHS:
            urls_to_check.append(f"{base}{path}")

        for url in urls_to_check:
            try:
                resp = self.session.get(url, timeout=10, allow_redirects=True)
                if resp.status_code != 200:
                    continue

                found = EMAIL_REGEX.findall(resp.text)
                for email in found:
                    email_lower = email.lower()
                    email_domain = email_lower.split("@")[1]

                    if email_domain in BLACKLISTED_EMAIL_DOMAINS:
                        continue
                    if any(bl in email_domain for bl in BLACKLISTED_EMAIL_DOMAINS):
                        continue

                    cleaned = clean_email(email_lower)
                    if cleaned:
                        emails.add(cleaned)

                time.sleep(0.5)

            except requests.RequestException:
                continue

        if not emails:
            return []

        # Prioritize emails matching the business website domain
        matching = [e for e in emails if site_domain and site_domain in e.split("@")[1]]
        if matching:
            return matching
        return list(emails)

    def find_business_phone(self, website_url: str) -> str | None:
        try:
            resp = self.session.get(website_url, timeout=10, allow_redirects=True)
            if resp.status_code != 200:
                return None

            phones = PHONE_REGEX.findall(resp.text)
            if phones:
                return clean_phone(phones[0])
        except requests.RequestException:
            pass
        return None

    def enrich_business(self, business: dict) -> dict:
        website = business.get("website")
        if not website:
            return business

        console.print(f"  [dim]Enriching: {website}[/dim]")

        if not business.get("email"):
            emails = self.find_business_emails(website)
            if emails:
                business["email"] = emails[0]
                console.print(f"    [green]Found email: {emails[0]}[/green]")

        if not business.get("phone"):
            phone = self.find_business_phone(website)
            if phone:
                business["phone"] = phone

        time.sleep(SCRAPE_DELAY)
        return business
