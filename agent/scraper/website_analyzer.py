import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from rich.console import Console

from ..config import PAGESPEED_API_KEY

console = Console()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

SOCIAL_DOMAINS = {
    "facebook.com": "Facebook",
    "instagram.com": "Instagram",
    "twitter.com": "Twitter",
    "x.com": "Twitter",
    "linkedin.com": "LinkedIn",
    "youtube.com": "YouTube",
    "tiktok.com": "TikTok",
    "pinterest.com": "Pinterest",
}

ANALYTICS_PATTERNS = [
    "google-analytics.com", "googletagmanager.com", "gtag(",
    "analytics.js", "ga.js", "fbq(", "hotjar.com",
    "mixpanel.com", "segment.com", "plausible.io",
]

CHAT_WIDGET_PATTERNS = [
    "intercom", "drift", "tawk", "crisp.chat", "livechat",
    "zendesk", "hubspot", "tidio", "olark", "freshchat",
    "chatwoot",
]

FORM_INDICATORS = [
    "contact", "get-in-touch", "reach-out", "send-message",
    "inquiry", "enquiry",
]

SEO_WEIGHTS = {
    "has_proper_title": 15,
    "has_meta_description": 15,
    "has_h1": 10,
    "has_alt_tags": 10,
    "has_sitemap": 10,
    "has_robots_txt": 5,
    "has_canonical": 10,
    "has_structured_data": 10,
    "has_open_graph": 10,
    "has_ssl": 5,
}

OVERALL_WEIGHTS = {
    "seo_score": 30,
    "page_speed_score": 25,
    "is_mobile_friendly": 15,
    "has_analytics": 5,
    "has_social_links": 5,
    "has_contact_form": 5,
    "has_favicon": 5,
    "has_responsive_design": 10,
}


class WebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def analyze(self, url: str) -> dict:
        console.print(f"[cyan]Auditing:[/cyan] {url}")

        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        result = self._empty_result()
        issues: list[dict] = []
        recommendations: list[str] = []

        html = None
        soup = None
        response = None
        load_start = time.time()

        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            load_time = time.time() - load_start
            result["load_time_seconds"] = round(load_time, 2)
            html = response.text
            soup = BeautifulSoup(html, "lxml")
        except requests.exceptions.SSLError:
            result["has_ssl"] = False
            issues.append({
                "issue": "SSL Certificate Error",
                "impact": "high",
                "category": "security",
                "description": "Your website has an invalid or expired SSL certificate. Visitors see a security warning before reaching your site.",
                "recommendation": "Install a valid SSL certificate. Most hosting providers offer free SSL via Let's Encrypt.",
                "business_impact": "Up to 85% of visitors will leave immediately when they see a 'Not Secure' warning, and Google penalizes your search rankings.",
            })
            try:
                response = self.session.get(
                    url.replace("https://", "http://"),
                    timeout=15,
                    allow_redirects=True,
                    verify=False,
                )
                load_time = time.time() - load_start
                result["load_time_seconds"] = round(load_time, 2)
                html = response.text
                soup = BeautifulSoup(html, "lxml")
            except requests.RequestException:
                result["issues"] = issues
                result["overall_score"] = 0
                return result
        except requests.RequestException as e:
            console.print(f"[red]  Cannot reach {url}: {e}[/red]")
            issues.append({
                "issue": "Website Unreachable",
                "impact": "high",
                "category": "technical",
                "description": f"Your website could not be loaded: {e}",
                "recommendation": "Check your hosting and DNS settings. Make sure your website is online.",
                "business_impact": "Every minute your website is down, you're losing potential customers who can't find or contact you.",
            })
            result["issues"] = issues
            result["overall_score"] = 0
            return result

        self._check_ssl(url, response, result, issues)
        self._check_title(soup, result, issues)
        self._check_meta_description(soup, result, issues)
        self._check_h1(soup, result, issues)
        self._check_alt_tags(soup, result, issues)
        self._check_mobile_friendly(soup, result, issues)
        self._check_favicon(soup, url, result, issues)
        self._check_sitemap(url, result, issues)
        self._check_robots_txt(url, result, issues)
        self._check_analytics(html, result, issues)
        self._check_social_links(soup, result, issues)
        self._check_open_graph(soup, result, issues)
        self._check_contact_form(soup, html, result, issues)
        self._check_chat_widget(html, result, issues)
        self._check_structured_data(soup, html, result, issues)
        self._check_responsive_design(soup, html, result, issues)
        self._check_headers(response, result, issues)
        self._check_heading_hierarchy(soup, result, issues)
        self._check_accessibility(soup, result, issues)
        self._check_page_speed(url, result, issues)

        seo_score = self._calc_seo_score(result)
        result["seo_score"] = seo_score
        result["overall_score"] = self._calc_overall_score(result)
        result["issues"] = issues
        result["recommendations"] = [i["recommendation"] for i in issues[:10]]

        console.print(
            f"  [bold]Score: {result['overall_score']}/100[/bold] "
            f"| SEO: {seo_score}/100 "
            f"| Issues: {len(issues)}"
        )

        return result

    # ------------------------------------------------------------------ checks

    def _check_ssl(self, url: str, response, result: dict, issues: list) -> None:
        if result.get("has_ssl") is False:
            return

        is_https = response.url.startswith("https://")
        result["has_ssl"] = is_https

        if not is_https:
            issues.append({
                "issue": "No HTTPS / SSL",
                "impact": "high",
                "category": "security",
                "description": "Your website doesn't use HTTPS. Modern browsers mark it as 'Not Secure'.",
                "recommendation": "Install an SSL certificate and redirect all HTTP traffic to HTTPS.",
                "business_impact": "Google Chrome shows a 'Not Secure' warning to every visitor. This destroys trust and can reduce conversions by 30-40%.",
            })

    def _check_title(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        title_tag = soup.find("title")
        if not title_tag or not title_tag.string or not title_tag.string.strip():
            result["has_proper_title"] = False
            issues.append({
                "issue": "Missing Page Title",
                "impact": "high",
                "category": "seo",
                "description": "Your website doesn't have a <title> tag, which is the clickable headline in Google search results.",
                "recommendation": "Add a compelling title tag (30-60 characters) that includes your business name and primary keyword.",
                "business_impact": "Without a title, Google generates one for you — often poorly. You're losing control of your first impression in search results.",
            })
            return

        title = title_tag.string.strip()
        length = len(title)

        if length < 30 or length > 60:
            result["has_proper_title"] = False
            issues.append({
                "issue": f"Suboptimal Title Length ({length} chars)",
                "impact": "medium",
                "category": "seo",
                "description": f"Your title tag is {length} characters. Google displays 50-60 characters in search results.",
                "recommendation": f"Adjust your title to 30-60 characters. Current: \"{title[:60]}\"",
                "business_impact": "A truncated or too-short title reduces your click-through rate by 10-20% in search results.",
            })
        else:
            result["has_proper_title"] = True

    def _check_meta_description(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        meta = soup.find("meta", attrs={"name": "description"})
        if not meta or not meta.get("content", "").strip():
            result["has_meta_description"] = False
            issues.append({
                "issue": "Missing Meta Description",
                "impact": "high",
                "category": "seo",
                "description": "Your website doesn't have a meta description tag. This is the snippet shown in Google search results.",
                "recommendation": "Add a compelling meta description (120-160 characters) that describes your business and includes relevant keywords.",
                "business_impact": "You're likely losing 20-30% of potential clicks from Google because searchers can't see what your business offers.",
            })
            return

        desc = meta["content"].strip()
        length = len(desc)

        if length < 120 or length > 160:
            result["has_meta_description"] = True
            issues.append({
                "issue": f"Suboptimal Meta Description Length ({length} chars)",
                "impact": "low",
                "category": "seo",
                "description": f"Your meta description is {length} characters. Ideal length is 120-160.",
                "recommendation": f"Adjust to 120-160 characters for optimal display in search results.",
                "business_impact": "A truncated description may cut off your call-to-action in search results.",
            })
        else:
            result["has_meta_description"] = True

    def _check_h1(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        h1_tags = soup.find_all("h1")
        count = len(h1_tags)

        if count == 0:
            result["has_h1"] = False
            issues.append({
                "issue": "Missing H1 Heading",
                "impact": "high",
                "category": "seo",
                "description": "Your page doesn't have an H1 heading, which tells Google what your page is about.",
                "recommendation": "Add one clear H1 heading at the top of your page that describes your main offering.",
                "business_impact": "Without an H1, search engines struggle to understand your page topic, reducing your ranking potential.",
            })
        elif count > 1:
            result["has_h1"] = True
            issues.append({
                "issue": f"Multiple H1 Tags ({count} found)",
                "impact": "medium",
                "category": "seo",
                "description": f"Your page has {count} H1 headings. Best practice is exactly one.",
                "recommendation": "Keep one H1 for your main heading and change others to H2 or H3.",
                "business_impact": "Multiple H1 tags dilute your SEO focus and confuse search engines about your primary topic.",
            })
        else:
            result["has_h1"] = True

    def _check_alt_tags(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        images = soup.find_all("img")
        if not images:
            result["has_alt_tags"] = True
            return

        with_alt = sum(1 for img in images if img.get("alt", "").strip())
        pct = (with_alt / len(images)) * 100

        result["has_alt_tags"] = pct >= 80

        if pct < 80:
            missing = len(images) - with_alt
            issues.append({
                "issue": f"Missing Image Alt Text ({missing}/{len(images)} images)",
                "impact": "medium",
                "category": "seo",
                "description": f"Only {pct:.0f}% of your images have descriptive alt text.",
                "recommendation": "Add descriptive alt text to all images describing what they show.",
                "business_impact": "Images without alt text can't appear in Google Image search, and your site is less accessible to visually impaired users.",
            })

    def _check_mobile_friendly(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        viewport = soup.find("meta", attrs={"name": "viewport"})
        result["is_mobile_friendly"] = viewport is not None

        if not viewport:
            issues.append({
                "issue": "Not Mobile-Friendly",
                "impact": "high",
                "category": "ux",
                "description": "Your website doesn't have a viewport meta tag, meaning it won't display correctly on phones.",
                "recommendation": 'Add <meta name="viewport" content="width=device-width, initial-scale=1"> to your page head.',
                "business_impact": "Over 60% of web traffic is mobile. Without mobile optimization, you're turning away the majority of potential customers.",
            })

    def _check_favicon(self, soup: BeautifulSoup, url: str, result: dict, issues: list) -> None:
        favicon = soup.find("link", rel=lambda x: x and "icon" in x)
        if favicon:
            result["has_favicon"] = True
            return

        try:
            base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
            resp = self.session.head(f"{base}/favicon.ico", timeout=5)
            result["has_favicon"] = resp.status_code == 200
        except requests.RequestException:
            result["has_favicon"] = False

        if not result["has_favicon"]:
            issues.append({
                "issue": "Missing Favicon",
                "impact": "low",
                "category": "ux",
                "description": "Your website doesn't have a favicon (the small icon in browser tabs).",
                "recommendation": "Add a favicon that matches your logo. Use a 32x32 PNG or ICO file.",
                "business_impact": "A missing favicon looks unprofessional and makes your site harder to find among open browser tabs.",
            })

    def _check_sitemap(self, url: str, result: dict, issues: list) -> None:
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        try:
            resp = self.session.get(f"{base}/sitemap.xml", timeout=5)
            result["has_sitemap"] = resp.status_code == 200 and "xml" in resp.text[:500].lower()
        except requests.RequestException:
            result["has_sitemap"] = False

        if not result["has_sitemap"]:
            issues.append({
                "issue": "Missing XML Sitemap",
                "impact": "medium",
                "category": "seo",
                "description": "No sitemap.xml found at /sitemap.xml. A sitemap helps Google discover all your pages.",
                "recommendation": "Generate and submit an XML sitemap to help search engines crawl your site efficiently.",
                "business_impact": "Without a sitemap, some of your pages may never appear in Google search results.",
            })

    def _check_robots_txt(self, url: str, result: dict, issues: list) -> None:
        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        try:
            resp = self.session.get(f"{base}/robots.txt", timeout=5)
            result["has_robots_txt"] = resp.status_code == 200 and len(resp.text.strip()) > 0
        except requests.RequestException:
            result["has_robots_txt"] = False

        if not result["has_robots_txt"]:
            issues.append({
                "issue": "Missing robots.txt",
                "impact": "low",
                "category": "seo",
                "description": "No robots.txt file found. This file controls how search engines crawl your site.",
                "recommendation": "Create a robots.txt file that references your sitemap and sets crawl rules.",
                "business_impact": "Search engines may crawl your site inefficiently, wasting crawl budget on unimportant pages.",
            })

    def _check_analytics(self, html: str, result: dict, issues: list) -> None:
        html_lower = html.lower()
        found = any(pattern in html_lower for pattern in ANALYTICS_PATTERNS)
        result["has_analytics"] = found

        if not found:
            issues.append({
                "issue": "No Analytics Tracking",
                "impact": "high",
                "category": "marketing",
                "description": "No analytics tracking code detected (Google Analytics, Tag Manager, etc.).",
                "recommendation": "Install Google Analytics (free) to track visitors, traffic sources, and popular pages.",
                "business_impact": "You're flying blind — you have no idea how many people visit your site, where they come from, or what they do. This makes marketing impossible to optimize.",
            })

    def _check_social_links(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        links = soup.find_all("a", href=True)
        found_socials: list[str] = []

        for link in links:
            href = link["href"].lower()
            for domain, name in SOCIAL_DOMAINS.items():
                if domain in href and name not in found_socials:
                    found_socials.append(name)

        result["has_social_links"] = len(found_socials) > 0

        if not found_socials:
            issues.append({
                "issue": "No Social Media Links",
                "impact": "medium",
                "category": "marketing",
                "description": "Your website doesn't link to any social media profiles.",
                "recommendation": "Add links to your active social media profiles (at minimum Facebook and Instagram).",
                "business_impact": "Social proof is critical — 71% of consumers who have a positive social media experience with a brand recommend it to others.",
            })

    def _check_open_graph(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        og_tags = soup.find_all("meta", property=lambda x: x and x.startswith("og:"))
        result["has_open_graph"] = len(og_tags) >= 3

        if len(og_tags) < 3:
            issues.append({
                "issue": "Missing Open Graph Tags",
                "impact": "medium",
                "category": "seo",
                "description": "Your site lacks Open Graph tags, which control how your links appear when shared on social media.",
                "recommendation": "Add og:title, og:description, og:image, and og:url meta tags.",
                "business_impact": "When someone shares your website on Facebook or LinkedIn, it shows a plain text link instead of a rich preview with image and description.",
            })

    def _check_contact_form(self, soup: BeautifulSoup, html: str, result: dict, issues: list) -> None:
        forms = soup.find_all("form")
        has_form = False

        for form in forms:
            form_text = form.get_text().lower()
            form_html = str(form).lower()
            if any(indicator in form_text or indicator in form_html for indicator in FORM_INDICATORS):
                has_form = True
                break

            inputs = form.find_all("input")
            textareas = form.find_all("textarea")
            if textareas or len(inputs) >= 3:
                input_types = {inp.get("type", "text").lower() for inp in inputs}
                if "email" in input_types or "tel" in input_types:
                    has_form = True
                    break

        result["has_contact_form"] = has_form

        if not has_form:
            issues.append({
                "issue": "No Contact Form",
                "impact": "high",
                "category": "ux",
                "description": "No contact form was detected on your website.",
                "recommendation": "Add a simple contact form on your homepage or a dedicated contact page.",
                "business_impact": "Businesses with contact forms convert 2-3x more website visitors into leads than those with just a phone number or email address.",
            })

    def _check_chat_widget(self, html: str, result: dict, issues: list) -> None:
        html_lower = html.lower()
        found = any(pattern in html_lower for pattern in CHAT_WIDGET_PATTERNS)
        result["has_chat_widget"] = found

    def _check_structured_data(self, soup: BeautifulSoup, html: str, result: dict, issues: list) -> None:
        has_json_ld = bool(soup.find("script", type="application/ld+json"))
        has_microdata = bool(soup.find(attrs={"itemscope": True}))
        has_rdfa = bool(soup.find(attrs={"typeof": True}))

        result["has_structured_data"] = has_json_ld or has_microdata or has_rdfa

        if not result["has_structured_data"]:
            issues.append({
                "issue": "No Structured Data / Schema Markup",
                "impact": "medium",
                "category": "seo",
                "description": "Your site has no structured data (Schema.org markup), which helps Google show rich results.",
                "recommendation": "Add LocalBusiness schema markup with your name, address, phone, hours, and reviews.",
                "business_impact": "Businesses with schema markup can get rich snippets in Google (stars, hours, price range), which increase click-through rates by 20-30%.",
            })

    def _check_responsive_design(self, soup: BeautifulSoup, html: str, result: dict, issues: list) -> None:
        has_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
        has_media_queries = bool(re.search(r"@media\s*\(", html))

        responsive_frameworks = ["bootstrap", "tailwind", "foundation", "bulma"]
        has_framework = any(fw in html.lower() for fw in responsive_frameworks)

        result["has_responsive_design"] = has_viewport and (has_media_queries or has_framework)

    def _check_headers(self, response, result: dict, issues: list) -> None:
        headers = response.headers

        has_gzip = "gzip" in headers.get("Content-Encoding", "").lower()
        if not has_gzip:
            issues.append({
                "issue": "No GZIP Compression",
                "impact": "medium",
                "category": "performance",
                "description": "Your server doesn't use GZIP compression for responses.",
                "recommendation": "Enable GZIP compression on your web server to reduce page size by 60-80%.",
                "business_impact": "Without compression, your pages load slower. Every 1-second delay reduces conversions by 7%.",
            })

        has_csp = "Content-Security-Policy" in headers
        if not has_csp:
            issues.append({
                "issue": "Missing Content-Security-Policy Header",
                "impact": "low",
                "category": "security",
                "description": "Your site lacks a Content-Security-Policy header, which protects against XSS attacks.",
                "recommendation": "Add a Content-Security-Policy header to your server configuration.",
                "business_impact": "Your website is more vulnerable to cross-site scripting attacks that could steal customer data.",
            })

    def _check_heading_hierarchy(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        headings = soup.find_all(re.compile(r"^h[1-6]$"))
        if not headings:
            return

        levels = [int(h.name[1]) for h in headings]

        bad_jumps = 0
        for i in range(1, len(levels)):
            if levels[i] > levels[i - 1] + 1:
                bad_jumps += 1

        if bad_jumps > 2:
            issues.append({
                "issue": "Broken Heading Hierarchy",
                "impact": "low",
                "category": "seo",
                "description": f"Your heading structure has {bad_jumps} places where it skips levels (e.g., H1 → H3).",
                "recommendation": "Restructure headings to follow a logical H1 → H2 → H3 hierarchy.",
                "business_impact": "Poor heading structure makes your content harder for Google to understand and index properly.",
            })

    def _check_accessibility(self, soup: BeautifulSoup, result: dict, issues: list) -> None:
        html_tag = soup.find("html")
        has_lang = html_tag.get("lang") if html_tag else False

        if not has_lang:
            issues.append({
                "issue": "Missing Language Attribute",
                "impact": "low",
                "category": "accessibility",
                "description": 'Your HTML tag is missing the lang attribute (e.g., lang="en").',
                "recommendation": 'Add lang="en" (or appropriate language) to your <html> tag.',
                "business_impact": "Screen readers may mispronounce your content, and search engines may misidentify your language.",
            })

        skip_link = soup.find("a", href="#main-content") or soup.find("a", class_=re.compile(r"skip", re.I))
        if not skip_link:
            issues.append({
                "issue": "No Skip Navigation Link",
                "impact": "low",
                "category": "accessibility",
                "description": "Your site doesn't have a 'skip to content' link for keyboard users.",
                "recommendation": "Add a visually hidden skip link at the top of the page that jumps to main content.",
                "business_impact": "Users relying on keyboards or assistive technology will have a frustrating experience navigating your site.",
            })

    def _check_page_speed(self, url: str, result: dict, issues: list) -> None:
        try:
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {"url": url, "strategy": "mobile"}
            if PAGESPEED_API_KEY:
                params["key"] = PAGESPEED_API_KEY

            resp = self.session.get(api_url, params=params, timeout=60)
            if resp.status_code != 200:
                result["page_speed_score"] = None
                return

            data = resp.json()
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            perf = categories.get("performance", {})
            score = perf.get("score")

            if score is not None:
                speed_score = int(score * 100)
                result["page_speed_score"] = speed_score

                if speed_score < 50:
                    issues.append({
                        "issue": f"Very Slow Page Speed (Score: {speed_score}/100)",
                        "impact": "high",
                        "category": "performance",
                        "description": f"Your mobile page speed score is {speed_score}/100. Google considers anything below 50 as poor.",
                        "recommendation": "Optimize images, enable caching, minimize JavaScript, and consider a faster hosting provider.",
                        "business_impact": "53% of mobile users abandon a site that takes over 3 seconds to load. A slow site is costing you over half your visitors.",
                    })
                elif speed_score < 90:
                    issues.append({
                        "issue": f"Page Speed Needs Improvement (Score: {speed_score}/100)",
                        "impact": "medium",
                        "category": "performance",
                        "description": f"Your mobile page speed score is {speed_score}/100. There's room for improvement.",
                        "recommendation": "Optimize your largest images, defer non-critical JavaScript, and leverage browser caching.",
                        "business_impact": "Improving speed from {0} to 90+ could increase your conversion rate by 10-15%.".format(speed_score),
                    })

            audits = lighthouse.get("audits", {})
            fcp = audits.get("first-contentful-paint", {})
            if fcp.get("numericValue"):
                load_seconds = fcp["numericValue"] / 1000
                if result.get("load_time_seconds") is None or load_seconds > result["load_time_seconds"]:
                    result["load_time_seconds"] = round(load_seconds, 2)

        except Exception as e:
            console.print(f"  [yellow]PageSpeed API unavailable: {e}[/yellow]")

    # --------------------------------------------------------------- scoring

    def _calc_seo_score(self, result: dict) -> int:
        score = 0
        total_weight = 0

        checks = {
            "has_proper_title": result.get("has_proper_title"),
            "has_meta_description": result.get("has_meta_description"),
            "has_h1": result.get("has_h1"),
            "has_alt_tags": result.get("has_alt_tags"),
            "has_sitemap": result.get("has_sitemap"),
            "has_robots_txt": result.get("has_robots_txt"),
            "has_structured_data": result.get("has_structured_data"),
            "has_open_graph": result.get("has_open_graph"),
            "has_ssl": result.get("has_ssl"),
        }

        # Canonical isn't directly stored, give it credit if OG is present
        checks["has_canonical"] = result.get("has_open_graph", False)

        for key, weight in SEO_WEIGHTS.items():
            total_weight += weight
            if checks.get(key):
                score += weight

        return int((score / total_weight) * 100) if total_weight else 0

    def _calc_overall_score(self, result: dict) -> int:
        score = 0.0
        total_weight = 0.0

        seo = result.get("seo_score", 0) or 0
        speed = result.get("page_speed_score") or 50

        components = {
            "seo_score": seo,
            "page_speed_score": speed,
            "is_mobile_friendly": 100 if result.get("is_mobile_friendly") else 0,
            "has_analytics": 100 if result.get("has_analytics") else 0,
            "has_social_links": 100 if result.get("has_social_links") else 0,
            "has_contact_form": 100 if result.get("has_contact_form") else 0,
            "has_favicon": 100 if result.get("has_favicon") else 0,
            "has_responsive_design": 100 if result.get("has_responsive_design") else 0,
        }

        for key, weight in OVERALL_WEIGHTS.items():
            total_weight += weight
            score += (components.get(key, 0) / 100) * weight

        return int((score / total_weight) * 100) if total_weight else 0

    @staticmethod
    def _empty_result() -> dict:
        return {
            "has_ssl": None,
            "is_mobile_friendly": None,
            "page_speed_score": None,
            "seo_score": None,
            "has_meta_description": None,
            "has_proper_title": None,
            "has_h1": None,
            "has_alt_tags": None,
            "has_sitemap": None,
            "has_robots_txt": None,
            "has_analytics": None,
            "has_social_links": None,
            "has_contact_form": None,
            "has_chat_widget": None,
            "has_structured_data": None,
            "has_favicon": None,
            "has_open_graph": None,
            "has_responsive_design": None,
            "load_time_seconds": None,
            "issues": [],
            "recommendations": [],
            "overall_score": 0,
        }
