import re
from urllib.parse import urlparse

from ..config import PORTFOLIO_BASE_URL

_PHONE_DIGITS_RE = re.compile(r"\D")
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_SLUG_RE = re.compile(r"[^a-z0-9]+")

CATEGORY_MAP: dict[str, list[str]] = {
    "restaurant": [
        "restaurant", "food", "pizza", "sushi", "burger", "cafe", "coffee",
        "bakery", "bar", "grill", "diner", "bistro", "eatery", "taco",
        "thai", "chinese", "italian", "mexican", "indian", "japanese",
        "seafood", "steakhouse", "bbq", "barbecue", "fast food",
        "ice cream", "donut", "deli", "catering", "buffet",
    ],
    "healthcare": [
        "doctor", "medical", "clinic", "hospital", "health", "physician",
        "urgent care", "pharmacy", "therapist", "psychologist",
        "psychiatrist", "dermatolog", "pediatr", "orthoped", "cardiolog",
        "optometr", "ophthalmolog", "chiropract", "physical therap",
    ],
    "dental": [
        "dentist", "dental", "orthodont", "oral surgeon", "endodont",
        "periodont", "prosthodont",
    ],
    "retail": [
        "store", "shop", "boutique", "retail", "market", "mall",
        "clothing", "apparel", "fashion", "jewel", "gift", "florist",
        "flower", "furniture", "hardware", "pet store", "toy",
    ],
    "real_estate": [
        "real estate", "realtor", "property", "apartment", "housing",
        "mortgage", "home builder", "construction",
    ],
    "legal": [
        "lawyer", "attorney", "law firm", "legal", "notary",
        "immigration", "divorce", "criminal defense",
    ],
    "automotive": [
        "auto", "car", "mechanic", "body shop", "tire", "oil change",
        "car wash", "dealership", "vehicle", "motor", "transmission",
    ],
    "beauty": [
        "salon", "spa", "beauty", "hair", "nail", "barber", "wax",
        "lash", "brow", "skincare", "cosmetic", "tattoo", "piercing",
        "makeup", "aesthet",
    ],
    "fitness": [
        "gym", "fitness", "yoga", "pilates", "crossfit", "martial art",
        "boxing", "personal train", "sport", "swim", "dance studio",
    ],
    "education": [
        "school", "tutor", "education", "learning", "training",
        "preschool", "daycare", "child care", "academy", "college",
        "university", "driving school", "music lesson",
    ],
    "professional_services": [
        "accounting", "accountant", "cpa", "consulting", "financial",
        "insurance", "tax", "marketing", "advertising", "design",
        "architect", "engineer", "it service", "web design",
    ],
    "home_services": [
        "plumb", "electric", "hvac", "roof", "landscap", "clean",
        "pest control", "locksmith", "moving", "painting", "flooring",
        "remodel", "handyman", "garage door", "fencing", "pool",
        "window", "gutter", "siding", "solar", "tree service",
    ],
}


def extract_domain(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        domain = parsed.netloc or parsed.path.split("/")[0]
        return domain.lower().removeprefix("www.")
    except Exception:
        return ""


def clean_phone(phone: str) -> str:
    if not phone:
        return ""
    digits = _PHONE_DIGITS_RE.sub("", phone)
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return phone.strip()


_FAKE_EMAIL_PATTERNS = re.compile(
    r"@\d+x\.\w+$|"          # logo@2x.png, icon@3x.png
    r"\.(png|jpg|jpeg|gif|svg|webp|ico|bmp|tiff|css|js|map|woff|woff2|ttf|eot)$|"  # file extensions
    r"^(no-?reply|noreply|mailer-daemon|postmaster|webmaster|admin@localhost)",     # system emails
    re.IGNORECASE,
)

_JUNK_LOCAL_PARTS = {
    "name", "email", "your", "info@example", "user", "test",
    "username", "yourname", "youremail", "enter",
}


def clean_email(email: str) -> str | None:
    if not email:
        return None
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        return None
    if _FAKE_EMAIL_PATTERNS.search(email):
        return None
    local_part = email.split("@")[0]
    if local_part in _JUNK_LOCAL_PARTS:
        return None
    # Reject if TLD looks like a file extension or is too short
    tld = email.rsplit(".", 1)[-1]
    if len(tld) > 10 or tld in ("png", "jpg", "jpeg", "gif", "svg", "webp", "css", "js"):
        return None
    return email


def slugify(text: str) -> str:
    return _SLUG_RE.sub("-", text.lower()).strip("-")[:80]


def generate_portfolio_url(business_id: int, business_name: str) -> str:
    slug = slugify(business_name)
    return f"{PORTFOLIO_BASE_URL}/audit/{business_id}/{slug}"


def categorize_business(category: str) -> str:
    if not category:
        return "other"
    cat_lower = category.lower()
    for domain, keywords in CATEGORY_MAP.items():
        for keyword in keywords:
            if keyword in cat_lower:
                return domain
    return "other"
