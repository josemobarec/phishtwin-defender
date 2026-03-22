import re
from typing import List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup


URL_REGEX = re.compile(r"(https?://[^\s\"'<>]+)", re.IGNORECASE)


def safe_strip(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned if cleaned else None


def extract_domain(email_address: Optional[str]) -> Optional[str]:
    """
    Extrae el dominio desde una dirección tipo:
    - user@domain.com
    - Name <user@domain.com>
    """
    if not email_address:
        return None

    email_address = email_address.strip()

    if "<" in email_address and ">" in email_address:
        start = email_address.find("<") + 1
        end = email_address.find(">")
        email_address = email_address[start:end].strip()

    if "@" not in email_address:
        return None

    return email_address.split("@")[-1].lower()


def normalize_links(links: List[str]) -> List[str]:
    normalized = []
    seen = set()

    for link in links:
        if not link:
            continue

        cleaned = link.strip()
        if not cleaned:
            continue

        parsed = urlparse(cleaned)

        if not parsed.scheme or not parsed.netloc:
            continue

        normalized_link = cleaned.lower()

        if normalized_link not in seen:
            seen.add(normalized_link)
            normalized.append(normalized_link)

    return normalized


def extract_links_from_text(text: Optional[str]) -> List[str]:
    if not text:
        return []

    matches = URL_REGEX.findall(text)
    return normalize_links(matches)


def extract_links_from_html(html: Optional[str]) -> List[str]:
    if not html:
        return []

    links: List[str] = []

    try:
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup.find_all("a", href=True):
            href = tag.get("href")
            if href:
                links.append(href)

        # opcionalmente, también busca URLs visibles dentro del HTML
        visible_urls = URL_REGEX.findall(html)
        links.extend(visible_urls)

    except Exception:
        return []

    return normalize_links(links)

def extract_url_domain(url: Optional[str]) -> Optional[str]:
    if not url:
        return None

    try:
        parsed = urlparse(url.strip())
        if not parsed.netloc:
            return None
        return parsed.netloc.lower()
    except Exception:
        return None


def get_base_domain(domain: Optional[str]) -> Optional[str]:
    """
    Heurística simple para MVP:
    - intranet.internal-example.com -> internal-example.com
    - updates-example.com -> updates-example.com
    """
    if not domain:
        return None

    parts = domain.lower().split(".")
    if len(parts) < 2:
        return domain.lower()

    return ".".join(parts[-2:])