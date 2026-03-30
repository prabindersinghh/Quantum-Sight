"""
CBOM Builder — Maps scan data to all CERT-IN Annexure-A CBOM fields.
Generates complete Cryptographic Bill of Materials entries with all
22+ fields required for regulatory compliance.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Cipher primitive mapping
CIPHER_PRIMITIVES = {
    "RSA": "key_exchange",
    "ECDHE": "key_exchange",
    "DHE": "key_exchange",
    "ECDH": "key_exchange",
    "DH": "key_exchange",
    "AES": "encryption",
    "CHACHA20": "encryption",
    "3DES": "encryption",
    "DES": "encryption",
    "RC4": "encryption",
    "ECDSA": "signature",
    "DSA": "signature",
    "SHA": "hash",
    "MD5": "hash",
    "GCM": "aead",
    "POLY1305": "aead",
    "PSK": "key_exchange",
    "TLS_AES": "encryption",
    "ML-KEM": "kem",
    "ML-DSA": "signature",
    "SLH-DSA": "signature",
    "FALCON": "signature",
    "KYBER": "kem",
    "DILITHIUM": "signature",
}

# Mode mapping
MODE_MAP = {
    "GCM": "gcm",
    "CBC": "cbc",
    "CCM": "ccm",
    "ECB": "ecb",
    "CTR": "ctr",
    "CHACHA20": "stream",
    "POLY1305": "mac",
    "CFB": "cfb",
    "OFB": "ofb",
}

# Crypto functions by primitive type
CRYPTO_FUNCTIONS_MAP = {
    "encryption": ["encrypt", "decrypt"],
    "key_exchange": ["key_generation", "key_agreement", "key_derivation"],
    "signature": ["sign", "verify"],
    "hash": ["hash", "digest"],
    "aead": ["encrypt", "decrypt", "authenticate"],
    "kem": ["encapsulate", "decapsulate", "key_generation"],
}

# Protocol OIDs
PROTOCOL_OIDS = {
    "TLS 1.3": "1.3.18.0.2.26.141",
    "TLS 1.2": "1.3.18.0.2.26.140",
    "TLS 1.1": "1.3.18.0.2.26.139",
    "TLS 1.0": "1.3.18.0.2.26.138",
    "SSLv3": "1.3.6.1.5.5.7.1.99",
    "SSLv2": "1.3.6.1.5.5.7.1.98",
    "SSL 3.0": "1.3.6.1.5.5.7.1.99",
    "SSL 2.0": "1.3.6.1.5.5.7.1.98",
}


def build_cbom_entry(scan_data: dict) -> dict:
    """
    Build complete CBOM entry with all Annexure-A fields.
    Maps live TLS scan data to the CERT-IN CBOM specification.
    """
    cipher = scan_data.get("cipher_suite", "")
    tls_version = scan_data.get("tls_version", "")
    key_size = scan_data.get("cert_key_size", 0)
    key_type = scan_data.get("cert_key_type", "RSA")

    primitive = _detect_primitive(cipher)
    mode = _detect_mode(cipher)
    crypto_functions = CRYPTO_FUNCTIONS_MAP.get(primitive, ["encrypt", "decrypt"])
    classical_security = _classical_security_bits(cipher, key_size, key_type)
    algo_list = _get_algo_list(cipher)

    # Key state
    key_state = "expired" if scan_data.get("is_expired") else "active"

    # Subject CN extraction
    subject = scan_data.get("subject", "")
    key_name = _extract_cn(subject) or scan_data.get("hostname", "")

    return {
        # ── ALGORITHM fields (7 fields per Annexure-A) ──
        "algo_name": cipher,
        "algo_asset_type": "algorithm",
        "algo_primitive": primitive,
        "algo_mode": mode,
        "algo_crypto_functions": crypto_functions,
        "algo_classical_security_level": classical_security,
        "algo_oid": scan_data.get("signature_algorithm_oid", ""),
        "algo_list": algo_list,

        # ── KEY fields (5 fields per Annexure-A) ──
        "key_name": key_name,
        "key_asset_type": "key",
        "key_id": scan_data.get("serial_number", ""),
        "key_state": key_state,
        "key_size": key_size,
        "key_creation_date": scan_data.get("not_valid_before"),
        "key_activation_date": scan_data.get("not_valid_before"),

        # ── PROTOCOL fields (4 fields per Annexure-A) ──
        "protocol_name": "TLS",
        "protocol_asset_type": "protocol",
        "protocol_version": tls_version,
        "protocol_cipher_suites": cipher,
        "protocol_oid": _protocol_oid(tls_version),

        # ── CERTIFICATE fields (8 fields per Annexure-A) ──
        "cert_name": scan_data.get("hostname", ""),
        "cert_asset_type": "certificate",
        "cert_subject_name": scan_data.get("subject", ""),
        "cert_issuer_name": scan_data.get("issuer", ""),
        "cert_not_valid_before": scan_data.get("not_valid_before"),
        "cert_not_valid_after": scan_data.get("not_valid_after"),
        "cert_signature_algorithm_ref": scan_data.get("signature_algorithm", ""),
        "cert_subject_public_key_ref": _public_key_ref(key_type, key_size),
        "cert_format": "X.509",
        "cert_extension": ".crt",
        "cert_sha256_fingerprint": scan_data.get("sha256_fingerprint", ""),
        "cert_sha1_fingerprint": scan_data.get("sha1_fingerprint", ""),

        # ── METADATA ──
        "hostname": scan_data.get("hostname", ""),
        "scan_time": scan_data.get("scan_time"),
        "days_until_expiry": scan_data.get("days_until_expiry", 0),
        "is_expired": scan_data.get("is_expired", False),
    }


def _detect_primitive(cipher: str) -> str:
    c = cipher.upper()
    if any(k in c for k in ["ML-DSA", "DILITHIUM", "ECDSA", "DSA", "FALCON", "SLH-DSA"]):
        return "signature"
    if any(k in c for k in ["ML-KEM", "KYBER", "ECDHE", "DHE", "ECDH", "DH"]):
        return "key_exchange"
    if any(k in c for k in ["AES", "CHACHA20", "3DES", "DES", "RC4"]):
        return "encryption"
    if any(k in c for k in ["SHA", "MD5"]):
        return "hash"
    if "GCM" in c or "POLY1305" in c:
        return "aead"
    return "encryption"


def _detect_mode(cipher: str) -> str:
    c = cipher.upper()
    for key, val in MODE_MAP.items():
        if key in c:
            return val
    return "unknown"


def _classical_security_bits(cipher: str, key_size: int, key_type: str = "RSA") -> int:
    c = cipher.upper()
    if "AES-256" in c: return 256
    if "AES-128" in c: return 128
    if "CHACHA20" in c: return 256
    if key_type == "RSA" or "RSA" in c:
        if key_size >= 4096: return 140
        if key_size >= 3072: return 128
        if key_size >= 2048: return 112
        if key_size >= 1024: return 80
        return 56
    if key_type == "EC" or "ECDSA" in c or "ECDH" in c:
        if key_size >= 521: return 260
        if key_size >= 384: return 192
        if key_size >= 256: return 128
        return 80
    if "3DES" in c: return 112
    if "DES" in c: return 56
    if "RC4" in c: return 40
    return 112


def _get_algo_list(cipher: str) -> list:
    c = cipher.upper()
    algorithms = []
    known = ["RSA", "ECDHE", "DHE", "ECDSA", "AES-256-GCM", "AES-128-GCM",
             "AES-256-CBC", "AES-128-CBC", "CHACHA20-POLY1305", "SHA384",
             "SHA256", "SHA", "3DES", "RC4", "MD5", "ML-KEM", "ML-DSA",
             "SLH-DSA", "FALCON", "KYBER", "DILITHIUM"]
    for algo in known:
        if algo in c:
            algorithms.append(algo)
    if not algorithms:
        algorithms = [cipher]
    return algorithms


def _protocol_oid(tls_version: str) -> str:
    return PROTOCOL_OIDS.get(tls_version, "1.3.6.1.5.5.7.1.0")


def _public_key_ref(key_type: str, key_size: int) -> str:
    if key_type == "EC":
        return f"EC-{key_size}"
    if key_type == "DSA":
        return f"DSA-{key_size}"
    return f"RSA-{key_size}"


def _extract_cn(dn: str) -> Optional[str]:
    """Extract CN value from a DN string like 'CN=example.com,O=Org'."""
    if not dn:
        return None
    for part in dn.split(","):
        part = part.strip()
        if part.upper().startswith("CN="):
            return part[3:]
    return None
