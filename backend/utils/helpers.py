"""
Utility helpers for QuantumSight backend.
"""
import re
import uuid
from datetime import datetime, timezone
from typing import Optional


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def success_response(data=None, message: str = "OK") -> dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": utc_now()
    }


def error_response(message: str, data=None) -> dict:
    return {
        "success": False,
        "data": data,
        "message": message,
        "timestamp": utc_now()
    }


def clean_hostname(hostname: str) -> str:
    """Strip protocol prefixes and trailing slashes from a hostname."""
    hostname = hostname.strip()
    for prefix in ["https://", "http://", "ftp://"]:
        if hostname.lower().startswith(prefix):
            hostname = hostname[len(prefix):]
    hostname = hostname.split("/")[0].split("?")[0].split("#")[0]
    return hostname.lower()


def is_valid_hostname(hostname: str) -> bool:
    """Basic hostname/domain validation."""
    if not hostname:
        return False
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, hostname))


def extract_issuer_org(issuer_dn: str) -> str:
    """Extract organization name from issuer DN string."""
    if not issuer_dn:
        return "Unknown CA"
    for part in issuer_dn.split(","):
        part = part.strip()
        if part.upper().startswith("O="):
            org = part[2:].strip('"')
            # Normalize known CAs
            ca_names = {
                "digicert": "DigiCert",
                "lets encrypt": "Let's Encrypt",
                "comodo": "COMODO",
                "sectigo": "Sectigo",
                "globalsign": "GlobalSign",
                "entrust": "Entrust",
                "verisign": "VeriSign",
                "symantec": "Symantec",
                "thawte": "Thawte",
                "geotrust": "GeoTrust",
            }
            for key, name in ca_names.items():
                if key in org.lower():
                    return name
            return org
    # Try CN
    for part in issuer_dn.split(","):
        part = part.strip()
        if part.upper().startswith("CN="):
            return part[3:]
    return "Unknown CA"


def risk_to_color(risk_level: str) -> str:
    colors = {
        "CRITICAL": "#DC2626",
        "HIGH": "#EA580C",
        "MEDIUM": "#D97706",
        "LOW": "#65A30D",
        "SAFE": "#16A34A",
    }
    return colors.get(risk_level.upper(), "#6B7280")


def tier_to_color(tier: str) -> str:
    colors = {
        "Elite-PQC": "#16A34A",
        "Standard": "#2563EB",
        "Legacy": "#D97706",
        "Critical": "#DC2626",
    }
    return colors.get(tier, "#6B7280")
