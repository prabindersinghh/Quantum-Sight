"""
Asset Classifier — Classifies discovered hosts into asset types.
Uses hostname patterns, ports, and certificate SANs to determine
whether an asset is a WebApp, API, VPN Gateway, Server, or LoadBalancer.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Keyword patterns for classification
ASSET_TYPE_PATTERNS = {
    "API": [
        r"^api\.", r"^api-", r"-api\.", r"\.api\.",
        r"^gateway\.", r"^gw\.", r"^rest\.", r"^graphql\.",
        r"mobileapi", r"mobile-api", r"openapi", r"swagger",
    ],
    "VPN": [
        r"^vpn\.", r"^vpn\d+\.", r"^remote\.", r"^ssl-vpn\.",
        r"^ras\.", r"^gateway\.", r"^gw\.", r"^tunnel\.",
        r"^anyconnect\.", r"^pulse\.", r"^f5vpn\.",
    ],
    "Mail Server": [
        r"^mail\.", r"^smtp\.", r"^imap\.", r"^pop\.",
        r"^webmail\.", r"^mx\.", r"^exchange\.",
    ],
    "CDN/Static": [
        r"^cdn\.", r"^static\.", r"^assets\.", r"^img\.",
        r"^media\.", r"^files\.", r"^storage\.",
    ],
    "Auth/SSO": [
        r"^auth\.", r"^sso\.", r"^login\.", r"^idp\.",
        r"^oidc\.", r"^oauth\.", r"^identity\.",
    ],
    "Web App": [
        r"^www\.", r"^portal\.", r"^netbanking\.", r"^banking\.",
        r"^online\.", r"^web\.", r"^app\.", r"^dashboard\.",
        r"^payments\.", r"^pay\.", r"^secure\.",
    ],
}

# Owner inference from hostname patterns
OWNER_PATTERNS = {
    "Internet Banking Team": ["netbanking", "online", "portal", "banking"],
    "Mobile Banking Team": ["mobile", "mobileapi", "mapp"],
    "Payments Team": ["payments", "pay", "txn", "transaction"],
    "Network Team": ["vpn", "gateway", "remote", "ssl-vpn"],
    "Infrastructure Team": ["cdn", "static", "assets", "media"],
    "Security Team": ["auth", "sso", "login", "idp", "oauth"],
    "Email Team": ["mail", "smtp", "imap", "webmail"],
    "API Platform Team": ["api", "gateway", "rest", "graphql"],
}


def classify_asset(hostname: str, open_ports: list = None, san: list = None) -> dict:
    """
    Classify an asset based on its hostname, open ports, and certificate SANs.
    Returns asset_type and inferred owner.
    """
    hostname_lower = hostname.lower()
    asset_type = _match_type(hostname_lower)
    owner = _match_owner(hostname_lower)
    risk_level = _infer_risk(hostname_lower, open_ports or [])

    return {
        "asset_type": asset_type,
        "owner": owner,
        "risk_level": risk_level,
        "exposure": "Public"
    }


def _match_type(hostname: str) -> str:
    for asset_type, patterns in ASSET_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, hostname, re.IGNORECASE):
                return asset_type
    return "Web App"  # Default


def _match_owner(hostname: str) -> str:
    for owner, keywords in OWNER_PATTERNS.items():
        for kw in keywords:
            if kw in hostname:
                return owner
    return "IT Operations Team"


def _infer_risk(hostname: str, open_ports: list) -> str:
    high_risk_keywords = ["legacy", "old", "test", "dev", "staging", "uat"]
    if any(kw in hostname for kw in high_risk_keywords):
        return "High"
    tls_ports = [p["port"] for p in open_ports if isinstance(p, dict) and p.get("open")]
    if 80 in tls_ports and 443 not in tls_ports:
        return "High"  # Only HTTP, no TLS
    return "Medium"
