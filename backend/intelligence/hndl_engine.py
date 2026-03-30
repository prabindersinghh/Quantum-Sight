"""
HNDL Risk Engine — Calculates Harvest Now, Decrypt Later risk windows.
Computes per-asset risk based on classical security bits and CRQC timeline
estimates from NIST/ENISA (2030–2035).

This is QuantumSight's signature feature: showing exactly WHEN intercepted
banking traffic becomes decryptable by quantum computers.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# CRQC (Cryptographically Relevant Quantum Computer) timeline estimates
CRQC_TIMELINE = {
    "optimistic": 2030,   # Most aggressive estimate
    "median": 2033,       # NIST/ENISA consensus estimate
    "conservative": 2036, # Conservative estimate
}

CURRENT_YEAR = datetime.now().year


def calculate_hndl_risk(scan_data: dict, pqc_data: dict) -> dict:
    """
    Calculate Harvest Now, Decrypt Later risk window per asset.
    Based on cipher classical security bits and CRQC timeline estimates.
    Returns risk level, score, years until threat, and urgency messaging.
    """
    # PQC-ready assets have no HNDL risk
    if pqc_data.get("pqc_ready"):
        return {
            "hndl_risk_level": "SAFE",
            "hndl_risk_score": 0,
            "years_until_threat": None,
            "estimated_breach_year": None,
            "classical_security_bits": None,
            "risk_color": "green",
            "risk_description": (
                "Asset implements quantum-safe cryptography. "
                "HNDL threat fully mitigated."
            ),
            "urgency": "None — quantum-safe",
            "crqc_timeline_used": "median",
            "data_sensitivity_window": "Not applicable — PQC protected",
            "harvest_active": False
        }

    cipher = scan_data.get("cipher_suite", "").upper()
    key_size = scan_data.get("cert_key_size", 0)
    key_type = scan_data.get("cert_key_type", "RSA")
    tls_version = scan_data.get("tls_version", "TLS 1.2")

    # Calculate classical security level
    classical_bits = _classical_security_bits(cipher, key_size, key_type)

    # Estimate year when CRQC can decrypt this cipher
    breach_year = _estimate_breach_year(classical_bits, tls_version)
    years_remaining = breach_year - CURRENT_YEAR

    # Assign risk tier
    risk_level, risk_score, urgency, color = _assign_risk_tier(
        tls_version, key_size, cipher, years_remaining
    )

    return {
        "hndl_risk_level": risk_level,
        "hndl_risk_score": risk_score,
        "years_until_threat": max(0, years_remaining),
        "estimated_breach_year": breach_year,
        "classical_security_bits": classical_bits,
        "risk_color": color,
        "risk_description": _build_description(
            cipher, breach_year, years_remaining, risk_level
        ),
        "urgency": urgency,
        "crqc_timeline_used": "median",
        "data_sensitivity_window": f"{CURRENT_YEAR}–{breach_year}",
        "harvest_active": True,  # Adversaries may already be harvesting
        "harvest_warning": (
            f"WARNING: Intercepted traffic encrypted with {cipher} "
            f"may be decryptable by ~{breach_year} using a CRQC."
        )
    }


def _classical_security_bits(cipher: str, key_size: int, key_type: str = "RSA") -> int:
    """Calculate classical security strength in bits for the given cipher."""
    if "AES-256" in cipher: return 256
    if "AES-128" in cipher: return 128
    if "CHACHA20" in cipher: return 256

    if key_type == "EC" or "ECDSA" in cipher or "ECDH" in cipher:
        if key_size >= 521: return 260
        if key_size >= 384: return 192
        if key_size >= 256: return 128
        if key_size >= 224: return 112
        return 80

    if key_type == "RSA" or "RSA" in cipher:
        if key_size >= 4096: return 140
        if key_size >= 3072: return 128
        if key_size >= 2048: return 112
        if key_size >= 1024: return 80
        return 56

    if "3DES" in cipher: return 112
    if "DES" in cipher: return 56
    if "RC4" in cipher: return 40
    if "MD5" in cipher: return 64

    return 112  # Default assumption


def _estimate_breach_year(classical_bits: int, tls_version: str) -> int:
    """
    Estimate the year when a CRQC could decrypt traffic protected by
    the given cipher strength. Based on NIST/ENISA quantum timeline.
    """
    tv = tls_version.upper()

    # Already-broken protocols — immediate risk
    if any(v in tv for v in ["SSL 2", "SSL 3", "SSLV2", "SSLV3"]):
        return CURRENT_YEAR

    if classical_bits <= 40:
        return CURRENT_YEAR          # RC4 / DES variants — already broken
    if classical_bits <= 56:
        return CURRENT_YEAR          # DES — classically breakable today
    if classical_bits <= 80:
        return CURRENT_YEAR + 1      # Near-term CRQC risk
    if classical_bits <= 112:
        return CRQC_TIMELINE["optimistic"] - 1   # ~2029
    if classical_bits <= 128:
        return CRQC_TIMELINE["median"]           # ~2033
    if classical_bits <= 192:
        return CRQC_TIMELINE["median"] + 3       # ~2036
    if classical_bits <= 256:
        return CRQC_TIMELINE["conservative"] + 4  # ~2040
    return CRQC_TIMELINE["conservative"] + 8     # ~2044


def _assign_risk_tier(
    tls_version: str, key_size: int, cipher: str, years_remaining: int
) -> tuple:
    """Return (risk_level, risk_score, urgency, color)."""
    tv = tls_version.upper()

    # Immediately critical
    if (any(v in tv for v in ["SSL 2", "SSL 3", "SSLV2", "SSLV3"])
            or ("RC4" in cipher or "DES" in cipher and "3DES" not in cipher)
            or (key_size > 0 and key_size < 1024)):
        return (
            "CRITICAL",
            100,
            "IMMEDIATE — isolate and replace today. Traffic may already be compromised.",
            "red"
        )

    if years_remaining <= 0:
        return ("CRITICAL", 100, "BREACH WINDOW OPEN — immediate replacement required", "red")
    if years_remaining <= 3:
        return ("CRITICAL", 95, "CRITICAL — replace within 3 months", "red")
    if years_remaining <= 5:
        return ("HIGH", 85, "URGENT — replace within 6 months", "red")
    if years_remaining <= 8:
        return ("HIGH", 70, "HIGH PRIORITY — migrate within 12 months", "orange")
    if years_remaining <= 12:
        return ("MEDIUM", 45, "MEDIUM — plan PQC migration within 2 years", "amber")
    return ("LOW", 20, "LOW — include in 3-year PQC roadmap", "yellow")


def _build_description(
    cipher: str, breach_year: int, years_remaining: int, risk_level: str
) -> str:
    if years_remaining <= 0:
        return (
            f"HNDL BREACH WINDOW OPEN: Traffic encrypted with {cipher} "
            f"is at risk of quantum decryption NOW. Adversaries harvesting "
            f"this data can decrypt it using current or near-term CRQCs."
        )
    return (
        f"Intercepted {cipher} traffic could be decrypted by ~{breach_year} "
        f"({years_remaining} years remaining). Adversaries may be harvesting "
        f"this encrypted data today for future quantum decryption."
    )
