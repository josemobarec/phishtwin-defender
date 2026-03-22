from typing import Optional


def safe_strip(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None

    cleaned = value.strip()
    return cleaned if cleaned else None


def extract_domain(email_address: Optional[str]) -> Optional[str]:
    """
    Extrae el dominio básico desde una dirección tipo user@domain.com.
    En este paso dejamos una versión simple; luego la mejoramos.
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