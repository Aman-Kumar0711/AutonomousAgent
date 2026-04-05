import time

from rich.console import Console
from serpapi import GoogleSearch

from ..config import MAX_RESULTS_PER_QUERY, SCRAPE_DELAY, SERPAPI_KEY
from ..utils.helpers import categorize_business, clean_phone

console = Console()

COUNTRY_CODES = {
    "us": "United States", "usa": "United States", "united states": "United States",
    "ca": "Canada", "canada": "Canada",
    "uk": "United Kingdom", "gb": "United Kingdom", "united kingdom": "United Kingdom",
    "nl": "Netherlands", "netherlands": "Netherlands",
    "de": "Germany", "germany": "Germany",
    "fr": "France", "france": "France",
    "au": "Australia", "australia": "Australia",
    "in": "India", "india": "India",
    "ae": "UAE", "uae": "UAE",
    "sg": "Singapore", "singapore": "Singapore",
}

COUNTRY_GL = {
    "United States": "us", "Canada": "ca", "United Kingdom": "uk",
    "Netherlands": "nl", "Germany": "de", "France": "fr",
    "Australia": "au", "India": "in", "UAE": "ae", "Singapore": "sg",
}


class GoogleMapsScraper:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or SERPAPI_KEY
        if not self.api_key:
            console.print(
                "[red]Error: SERPAPI_KEY not set. Add it to your .env file.[/red]"
            )

    def search_businesses(
        self,
        business_type: str,
        city: str,
        state: str = "",
        country: str = "us",
    ) -> list[dict]:
        country_name = COUNTRY_CODES.get(country.lower(), country)
        gl = COUNTRY_GL.get(country_name, "us")

        if state:
            query = f"{business_type} in {city}, {state}"
            location_label = f"{city}, {state}, {country_name}"
        else:
            query = f"{business_type} in {city}, {country_name}"
            location_label = f"{city}, {country_name}"

        console.print(f"[cyan]Searching Google Maps:[/cyan] {query}")

        results: list[dict] = []
        collected = 0
        start = 0

        while collected < MAX_RESULTS_PER_QUERY:
            try:
                params: dict = {
                    "engine": "google_maps",
                    "q": query,
                    "type": "search",
                    "api_key": self.api_key,
                    "start": start,
                    "gl": gl,
                    "hl": "en",
                }

                search = GoogleSearch(params)
                data = search.get_dict()

                if "error" in data:
                    console.print(f"[red]API error: {data['error']}[/red]")
                    break

                local_results = data.get("local_results", [])
                if not local_results:
                    console.print("[yellow]No more results found.[/yellow]")
                    break

                for item in local_results:
                    if collected >= MAX_RESULTS_PER_QUERY:
                        break

                    business = self._parse_result(item, country_name)
                    if business:
                        business["city"] = city
                        business["state"] = state
                        business["country"] = country_name
                        results.append(business)
                        collected += 1

                console.print(
                    f"  [green]Collected {collected} businesses[/green]"
                )

                start += len(local_results)
                if len(local_results) < 20:
                    break

                time.sleep(SCRAPE_DELAY)

            except Exception as e:
                console.print(f"[red]Error during search: {e}[/red]")
                break

        console.print(
            f"[bold green]Found {len(results)} businesses in {location_label}[/bold green]"
        )
        return results

    def _parse_result(self, item: dict, country: str = "United States") -> dict | None:
        name = item.get("title")
        if not name:
            return None

        website = item.get("website")
        address = item.get("address")
        phone = item.get("phone")
        rating = item.get("rating")
        reviews = item.get("reviews")

        raw_category = ""
        category = item.get("type")
        if not category:
            types = item.get("types")
            if types and isinstance(types, list):
                category = types[0]
        if isinstance(category, list):
            raw_category = category[0] if category else ""
        elif category:
            raw_category = str(category)

        return {
            "name": name,
            "website": website,
            "phone": clean_phone(phone) if phone else None,
            "address": address,
            "rating": float(rating) if rating else None,
            "review_count": int(reviews) if reviews else None,
            "category": raw_category,
            "domain": categorize_business(raw_category),
            "source": "google_maps",
        }
