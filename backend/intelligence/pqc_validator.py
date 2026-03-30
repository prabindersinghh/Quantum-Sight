"""
PQC Validator — Validates cryptographic assets against NIST FIPS 203/204/205.
Classifies assets as Elite-PQC, Standard, Legacy, or Critical and
identifies quantum vulnerabilities with recommended NIST replacements.
"""
import logging

logger = logging.getLogger(__name__)

# NIST FIPS 203/204/205/206 approved PQC algorithms
NIST_PQC_ALGORITHMS = {
    # Key Encapsulation Mechanisms — FIPS 203 (ML-KEM / Kyber)
    "ML-KEM-512": {"fips": "203", "security_level": 1, "type": "kem"},
    "ML-KEM-768": {"fips": "203", "security_level": 3, "type": "kem"},
    "ML-KEM-1024": {"fips": "203", "security_level": 5, "type": "kem"},
    "CRYSTALS-KYBER": {"fips": "203", "security_level": 3, "type": "kem"},
    "KYBER512": {"fips": "203", "security_level": 1, "type": "kem"},
    "KYBER768": {"fips": "203", "security_level": 3, "type": "kem"},
    "KYBER1024": {"fips": "203", "security_level": 5, "type": "kem"},
    "KYBER": {"fips": "203", "security_level": 3, "type": "kem"},

    # Digital Signatures — FIPS 204 (ML-DSA / Dilithium)
    "ML-DSA-44": {"fips": "204", "security_level": 2, "type": "signature"},
    "ML-DSA-65": {"fips": "204", "security_level": 3, "type": "signature"},
    "ML-DSA-87": {"fips": "204", "security_level": 5, "type": "signature"},
    "CRYSTALS-DILITHIUM": {"fips": "204", "security_level": 3, "type": "signature"},
    "DILITHIUM2": {"fips": "204", "security_level": 2, "type": "signature"},
    "DILITHIUM3": {"fips": "204", "security_level": 3, "type": "signature"},
    "DILITHIUM5": {"fips": "204", "security_level": 5, "type": "signature"},

    # Hash-based Signatures — FIPS 205 (SLH-DSA / SPHINCS+)
    "SLH-DSA-SHA2-128S": {"fips": "205", "security_level": 1, "type": "signature"},
    "SLH-DSA-SHA2-128F": {"fips": "205", "security_level": 1, "type": "signature"},
    "SLH-DSA-SHA2-192S": {"fips": "205", "security_level": 3, "type": "signature"},
    "SLH-DSA-SHA2-192F": {"fips": "205", "security_level": 3, "type": "signature"},
    "SLH-DSA-SHA2-256S": {"fips": "205", "security_level": 5, "type": "signature"},
    "SLH-DSA-SHA2-256F": {"fips": "205", "security_level": 5, "type": "signature"},
    "SLH-DSA-SHAKE-128S": {"fips": "205", "security_level": 1, "type": "signature"},
    "SLH-DSA-SHAKE-128F": {"fips": "205", "security_level": 1, "type": "signature"},
    "SLH-DSA-SHAKE-256F": {"fips": "205", "security_level": 5, "type": "signature"},
    "SPHINCS+": {"fips": "205", "security_level": 3, "type": "signature"},
    "SPHINCSPLUS": {"fips": "205", "security_level": 3, "type": "signature"},

    # FALCON — NIST selected (FIPS 206 draft)
    "FALCON-512": {"fips": "206", "security_level": 1, "type": "signature"},
    "FALCON-1024": {"fips": "206", "security_level": 5, "type": "signature"},
    "FALCON": {"fips": "206", "security_level": 3, "type": "signature"},
}

# Quantum-vulnerable classical algorithms
VULNERABLE_ALGORITHMS = {
    "RSA": {
        "quantum_vulnerable": True,
        "reason": "Shor's algorithm can factor RSA moduli in polynomial time on a CRQC"
    },
    "ECDSA": {
        "quantum_vulnerable": True,
        "reason": "Shor's algorithm breaks elliptic curve discrete logarithm problem"
    },
    "ECDH": {
        "quantum_vulnerable": True,
        "reason": "Quantum computers break elliptic curve Diffie-Hellman key exchange"
    },
    "DHE": {
        "quantum_vulnerable": True,
        "reason": "Quantum breaks finite-field Diffie-Hellman via discrete log"
    },
    "DH": {
        "quantum_vulnerable": True,
        "reason": "Quantum breaks discrete logarithm problem"
    },
    "DSA": {
        "quantum_vulnerable": True,
        "reason": "Quantum breaks discrete logarithm problem underlying DSA"
    },
    "RC4": {
        "quantum_vulnerable": True,
        "reason": "Already classically broken — stream cipher with critical weaknesses"
    },
    "3DES": {
        "quantum_vulnerable": True,
        "reason": "Classically weak (Sweet32 attack) + Grover's algorithm halves key strength"
    },
    "DES": {
        "quantum_vulnerable": True,
        "reason": "Classically broken — 56-bit key trivially brute-forced"
    },
    "MD5": {
        "quantum_vulnerable": True,
        "reason": "Classically broken hash — collision attacks demonstrated"
    },
    "SHA1": {
        "quantum_vulnerable": True,
        "reason": "Classically deprecated — collision attacks (SHAttered) demonstrated"
    },
}


def validate_pqc(scan_data: dict) -> dict:
    """
    Validate a scanned asset against NIST PQC standards.
    Returns PQC status, tier, vulnerability details, and recommendations.
    """
    cipher = scan_data.get("cipher_suite", "").upper()
    tls_version = scan_data.get("tls_version", "")
    key_size = scan_data.get("cert_key_size", 0)

    # Check if already implements PQC
    for algo_name, algo_info in NIST_PQC_ALGORITHMS.items():
        if algo_name.upper() in cipher:
            return {
                "pqc_ready": True,
                "pqc_status": "Elite-PQC",
                "fips_standard": f"FIPS {algo_info['fips']}",
                "nist_security_level": algo_info["security_level"],
                "quantum_vulnerable": False,
                "vulnerability_reason": None,
                "recommended_replacement": None,
                "gap_details": f"Asset implements NIST-standardized PQC algorithm: {algo_name}"
            }

    # Determine vulnerability reason
    vuln_reason = None
    for algo, info in VULNERABLE_ALGORITHMS.items():
        if algo in cipher:
            vuln_reason = info["reason"]
            break

    # Determine PQC tier by TLS version + key size
    status = _determine_tier(tls_version, key_size, cipher)

    # Recommend NIST PQC replacement
    replacement = _get_replacement(cipher)

    return {
        "pqc_ready": False,
        "pqc_status": status,
        "fips_standard": None,
        "nist_security_level": None,
        "quantum_vulnerable": True,
        "vulnerability_reason": vuln_reason,
        "recommended_replacement": replacement,
        "gap_details": (
            f"Using {cipher} — quantum-vulnerable. "
            f"Migrate to {replacement['algorithm']} ({replacement['fips']})"
        )
    }


def _determine_tier(tls_version: str, key_size: int, cipher: str) -> str:
    """Determine asset PQC tier based on TLS version and key strength."""
    tv = tls_version.upper()

    # SSL v2/v3 or extremely weak key = Critical
    if any(v in tv for v in ["SSL 2", "SSL 3", "SSLV2", "SSLV3", "SSLv2", "SSLv3"]):
        return "Critical"
    if "RC4" in cipher.upper() or "DES" in cipher.upper() and "3DES" not in cipher.upper():
        return "Critical"
    if key_size > 0 and key_size < 1024:
        return "Critical"

    # TLS 1.0 / 1.1 or weak key = Legacy
    if any(v in tv for v in ["TLS 1.0", "TLS 1.1", "TLSV1.0", "TLSV1.1"]):
        return "Legacy"
    if 0 < key_size < 2048:
        return "Legacy"

    # TLS 1.2 = Standard
    if "TLS 1.2" in tls_version or "TLSV1.2" in tv:
        return "Standard"

    # TLS 1.3 but no PQC = Standard (best possible without actual PQC)
    if "TLS 1.3" in tls_version or "TLSV1.3" in tv:
        return "Standard"

    return "Standard"


def _get_replacement(cipher: str) -> dict:
    """Return recommended NIST PQC replacement algorithm."""
    c = cipher.upper()

    if "RSA" in c or "ECDH" in c or "DHE" in c:
        return {
            "algorithm": "ML-KEM-768",
            "fips": "FIPS 203",
            "oid": "2.16.840.1.101.3.4.4.2",
            "purpose": "Key Encapsulation Mechanism",
            "security_level": 3,
            "library": "liboqs / BouncyCastle PQC",
            "migration_effort": "Medium"
        }
    elif "ECDSA" in c or "DSA" in c:
        return {
            "algorithm": "ML-DSA-65",
            "fips": "FIPS 204",
            "oid": "2.16.840.1.101.3.4.3.18",
            "purpose": "Digital Signature",
            "security_level": 3,
            "library": "liboqs / BouncyCastle PQC",
            "migration_effort": "Medium"
        }
    else:
        return {
            "algorithm": "SLH-DSA-SHA2-128S",
            "fips": "FIPS 205",
            "oid": "2.16.840.1.101.3.4.3.20",
            "purpose": "Hash-based Signature",
            "security_level": 1,
            "library": "liboqs",
            "migration_effort": "Low"
        }
