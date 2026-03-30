"""
Cyber Rating Engine — Assigns 0–1000 PQC Cyber Rating scores to assets.
Tiers: Critical (0–399), Legacy (400–699), Standard (700–849), Elite-PQC (850–1000).
Five weighted scoring dimensions with PQC readiness having highest weight (300 pts).
"""
import logging

logger = logging.getLogger(__name__)


def calculate_cyber_rating(scan_data: dict, pqc_data: dict, hndl_data: dict) -> dict:
    """
    Calculate 0–1000 PQC Cyber Rating for an asset.
    Returns total score, tier, breakdown per dimension, and tier description.
    """
    score = 0
    breakdown = {}

    # ── 1. TLS Version Score (max 200) ──────────────────────────────
    tls = scan_data.get("tls_version", "")
    tls_score, tls_detail = _score_tls_version(tls)
    score += tls_score
    breakdown["tls_version"] = {"score": tls_score, "max": 200, "detail": tls_detail}

    # ── 2. Cipher Strength Score (max 200) ──────────────────────────
    cipher = scan_data.get("cipher_suite", "").upper()
    cipher_score, cipher_detail = _score_cipher(cipher)
    score += cipher_score
    breakdown["cipher_strength"] = {"score": cipher_score, "max": 200, "detail": cipher_detail}

    # ── 3. Key Size Score (max 150) ─────────────────────────────────
    key_size = scan_data.get("cert_key_size", 0)
    key_type = scan_data.get("cert_key_type", "RSA")
    key_score, key_detail = _score_key_size(key_size, key_type)
    score += key_score
    breakdown["key_size"] = {"score": key_score, "max": 150, "detail": key_detail}

    # ── 4. Certificate Validity Score (max 150) ──────────────────────
    days_expiry = scan_data.get("days_until_expiry", 0)
    is_expired = scan_data.get("is_expired", False)
    cert_score, cert_detail = _score_cert_validity(is_expired, days_expiry)
    score += cert_score
    breakdown["cert_validity"] = {"score": cert_score, "max": 150, "detail": cert_detail}

    # ── 5. PQC Readiness Score (max 300 — highest weight) ───────────
    pqc_score, pqc_detail = _score_pqc_readiness(pqc_data)
    score += pqc_score
    breakdown["pqc_readiness"] = {"score": pqc_score, "max": 300, "detail": pqc_detail}

    total = min(score, 1000)

    # Determine tier
    tier, tier_color, tier_description = _determine_tier(total)

    return {
        "total_score": total,
        "tier": tier,
        "tier_color": tier_color,
        "tier_description": tier_description,
        "breakdown": breakdown,
        "max_score": 1000,
        "percentage": round((total / 1000) * 100, 1),
        "hndl_risk_level": hndl_data.get("hndl_risk_level", "UNKNOWN"),
        "estimated_breach_year": hndl_data.get("estimated_breach_year"),
        "years_until_threat": hndl_data.get("years_until_threat"),
    }


def _score_tls_version(tls: str) -> tuple:
    tv = tls.upper()
    if "1.3" in tv:
        return 200, "TLS 1.3 — optimal, modern protocol"
    if "1.2" in tv:
        return 140, "TLS 1.2 — acceptable, plan upgrade"
    if "1.1" in tv:
        return 60, "TLS 1.1 — deprecated (RFC 8996), replace immediately"
    if "1.0" in tv:
        return 20, "TLS 1.0 — deprecated and insecure (RFC 8996)"
    if any(v in tv for v in ["SSL 3", "SSL 2", "SSLV", "SSLv"]):
        return 0, "SSL — critically insecure, known broken protocols"
    return 80, f"Unknown protocol: {tls}"


def _score_cipher(cipher: str) -> tuple:
    c = cipher.upper()
    # PQC ciphers — top marks
    if any(pqc in c for pqc in ["ML-KEM", "ML-DSA", "SLH-DSA", "FALCON", "KYBER", "DILITHIUM"]):
        return 200, "NIST PQC cipher — quantum-safe encryption"
    # Strong modern AEAD ciphers
    if "CHACHA20" in c and "POLY1305" in c:
        return 200, "ChaCha20-Poly1305 — strong modern AEAD cipher"
    if "AES-256-GCM" in c:
        return 200, "AES-256-GCM — strong AEAD cipher"
    if "AES-256" in c and "GCM" in c:
        return 200, "AES-256-GCM — strong AEAD cipher"
    if "AES_256_GCM" in c:
        return 200, "AES-256-GCM — strong AEAD cipher (TLS 1.3)"
    if "TLS_AES_256" in c:
        return 200, "AES-256-GCM — strong AEAD cipher (TLS 1.3)"
    # Good AEAD ciphers
    if "AES-128-GCM" in c or "AES_128_GCM" in c or "TLS_AES_128" in c:
        return 160, "AES-128-GCM — good AEAD cipher"
    # CBC ciphers — weaker mode
    if "AES" in c and "CBC" in c:
        return 80, "AES-CBC — acceptable but weaker than GCM mode"
    if "AES" in c:
        return 100, "AES — good symmetric cipher, mode unspecified"
    # Broken/weak ciphers
    if "3DES" in c:
        return 20, "3DES — deprecated (RFC 7568), vulnerable to SWEET32"
    if "RC4" in c:
        return 0, "RC4 — classically broken, immediate replacement required"
    if "DES" in c and "3DES" not in c:
        return 0, "DES — classically broken, 56-bit key trivially brute-forced"
    if "NULL" in c:
        return 0, "NULL cipher — no encryption at all"
    if "EXPORT" in c:
        return 0, "EXPORT cipher — deliberately weakened (FREAK attack)"
    return 80, f"Cipher: {cipher[:50]}"


def _score_key_size(key_size: int, key_type: str) -> tuple:
    if key_size <= 0:
        return 50, "Key size unknown"

    if key_type == "EC":
        # EC keys are more efficient — smaller = equivalent
        if key_size >= 521:
            return 150, f"EC-{key_size} — P-521, excellent quantum margin"
        if key_size >= 384:
            return 140, f"EC-{key_size} — P-384, strong"
        if key_size >= 256:
            return 120, f"EC-{key_size} — P-256, good"
        if key_size >= 224:
            return 80, f"EC-{key_size} — acceptable minimum"
        return 20, f"EC-{key_size} — weak, below minimum recommendations"

    # RSA key scoring
    if key_size >= 4096:
        return 150, f"RSA-{key_size} — excellent, exceeds NIST recommendations"
    if key_size >= 3072:
        return 130, f"RSA-{key_size} — good, meets NIST 2030+ requirements"
    if key_size >= 2048:
        return 100, f"RSA-{key_size} — minimum acceptable per NIST SP 800-131A"
    if key_size >= 1024:
        return 30, f"RSA-{key_size} — weak, below NIST minimum (2048-bit)"
    return 0, f"RSA-{key_size} — critically weak, immediately replace"


def _score_cert_validity(is_expired: bool, days_expiry: int) -> tuple:
    if is_expired:
        return 0, "Certificate EXPIRED — immediate renewal required"
    if days_expiry < 7:
        return 0, f"CRITICAL: Expires in {days_expiry} days"
    if days_expiry < 30:
        return 20, f"WARNING: Expiring in {days_expiry} days — renew immediately"
    if days_expiry < 60:
        return 60, f"Expiring in {days_expiry} days — plan renewal"
    if days_expiry < 90:
        return 80, f"Expiring in {days_expiry} days — monitor"
    return 150, f"Valid for {days_expiry} days — good"


def _score_pqc_readiness(pqc_data: dict) -> tuple:
    if pqc_data.get("pqc_ready"):
        fips = pqc_data.get("fips_standard", "FIPS 203+")
        return 300, f"NIST PQC implemented ({fips}) — Elite-PQC"

    status = pqc_data.get("pqc_status", "Standard")
    if status == "Standard":
        return 100, "Standard classical crypto — not quantum-safe. PQC migration required."
    if status == "Legacy":
        return 30, "Legacy protocols (TLS 1.0/1.1) — quantum vulnerable. Urgent migration."
    if status == "Critical":
        return 0, "Critical — SSL/broken ciphers. Immediate action required."
    return 50, f"Status: {status}"


def _determine_tier(score: int) -> tuple:
    """Return (tier_name, tier_color, tier_description)."""
    if score >= 850:
        return (
            "Elite-PQC",
            "green",
            "Quantum-ready. Implements NIST PQC standards. Issue PQC-Ready Certificate."
        )
    if score >= 700:
        return (
            "Standard",
            "blue",
            "Good cryptographic posture. Plan PQC migration within 12–24 months."
        )
    if score >= 400:
        return (
            "Legacy",
            "amber",
            "Weak cryptographic posture. Remediation required within 6 months."
        )
    return (
        "Critical",
        "red",
        "Critically insecure. Immediate isolation and replacement required."
    )


def calculate_enterprise_rating(asset_ratings: list) -> dict:
    """Calculate consolidated enterprise-level PQC score from individual asset scores."""
    if not asset_ratings:
        return {"total_score": 0, "tier": "Unknown", "asset_count": 0}

    scores = [r.get("total_score", 0) for r in asset_ratings]
    avg_score = round(sum(scores) / len(scores))

    tier_counts = {"Elite-PQC": 0, "Standard": 0, "Legacy": 0, "Critical": 0}
    for r in asset_ratings:
        t = r.get("tier", "Standard")
        if t in tier_counts:
            tier_counts[t] += 1

    tier, color, description = _determine_tier(avg_score)

    return {
        "total_score": avg_score,
        "tier": tier,
        "tier_color": color,
        "tier_description": description,
        "asset_count": len(asset_ratings),
        "tier_distribution": tier_counts,
        "lowest_score": min(scores),
        "highest_score": max(scores),
        "pqc_ready_count": tier_counts["Elite-PQC"],
        "pqc_ready_percentage": round(tier_counts["Elite-PQC"] / len(asset_ratings) * 100, 1)
    }
