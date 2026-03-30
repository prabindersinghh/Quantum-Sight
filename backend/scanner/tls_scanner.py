"""
TLS Scanner — Core TLS handshake and certificate extraction module.
Performs live TLS handshakes against public-facing assets to extract
all cryptographic data required for CBOM Annexure-A field population.
"""
import ssl
import socket
import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa

logger = logging.getLogger(__name__)


async def scan_domain(hostname: str, port: int = 443) -> dict:
    """
    Perform full TLS handshake and extract ALL cryptographic data.
    Returns complete data for CBOM Annexure-A fields.
    Non-blocking — runs sync TLS logic in executor thread.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_scan, hostname, port)


def _sync_scan(hostname: str, port: int) -> dict:
    """Synchronous TLS scan — runs in executor thread."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with socket.create_connection((hostname, port), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cipher = ssock.cipher()          # (name, protocol, bits)
                cert_der = ssock.getpeercert(binary_form=True)

        if not cert_der:
            return _error_result(hostname, port, "No certificate returned")

        cert = x509.load_der_x509_certificate(cert_der, default_backend())

        # Extract public key info
        pub_key = cert.public_key()
        key_size = _get_key_size(pub_key)
        key_type = _get_key_type(pub_key)

        # Signature algorithm
        sig_algo_name = "unknown"
        try:
            sig_algo_name = cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else "unknown"
        except Exception:
            pass

        sig_algo_oid = str(cert.signature_algorithm_oid.dotted_string) if cert.signature_algorithm_oid else ""

        # Fingerprint
        sha256_fp = hashlib.sha256(cert_der).hexdigest()
        sha1_fp = hashlib.sha1(cert_der).hexdigest()

        # Validity
        now = datetime.now(timezone.utc)
        try:
            not_before = cert.not_valid_before_utc
            not_after = cert.not_valid_after_utc
        except AttributeError:
            # Older cryptography versions
            not_before = cert.not_valid_before.replace(tzinfo=timezone.utc)
            not_after = cert.not_valid_after.replace(tzinfo=timezone.utc)

        is_expired = now > not_after
        days_until_expiry = (not_after - now).days

        return {
            "hostname": hostname,
            "port": port,
            "scan_time": now.isoformat(),
            "tls_version": cipher[1] if cipher else "Unknown",
            "cipher_suite": cipher[0] if cipher else "Unknown",
            "key_bits": cipher[2] if cipher else 0,
            "cert_key_size": key_size,
            "cert_key_type": key_type,
            "signature_algorithm": sig_algo_name,
            "signature_algorithm_oid": sig_algo_oid,
            "subject": cert.subject.rfc4514_string(),
            "issuer": cert.issuer.rfc4514_string(),
            "not_valid_before": not_before.isoformat(),
            "not_valid_after": not_after.isoformat(),
            "serial_number": str(cert.serial_number),
            "sha256_fingerprint": sha256_fp,
            "sha1_fingerprint": sha1_fp,
            "cert_format": "X.509",
            "cert_extension": ".crt",
            "san": _get_san(cert),
            "is_expired": is_expired,
            "days_until_expiry": days_until_expiry,
            "scan_success": True,
            "error": None
        }

    except socket.timeout:
        return _error_result(hostname, port, "Connection timed out")
    except ConnectionRefusedError:
        return _error_result(hostname, port, "Connection refused — port may be closed")
    except ssl.SSLError as e:
        return _error_result(hostname, port, f"SSL error: {str(e)}")
    except Exception as e:
        return _error_result(hostname, port, str(e))


def _error_result(hostname: str, port: int, error: str) -> dict:
    return {
        "hostname": hostname,
        "port": port,
        "scan_success": False,
        "error": error,
        "scan_time": datetime.now(timezone.utc).isoformat(),
        "tls_version": "Unknown",
        "cipher_suite": "Unknown",
        "key_bits": 0,
        "cert_key_size": 0,
        "cert_key_type": "Unknown",
        "signature_algorithm": "unknown",
        "signature_algorithm_oid": "",
        "subject": "",
        "issuer": "",
        "not_valid_before": None,
        "not_valid_after": None,
        "serial_number": "",
        "sha256_fingerprint": "",
        "sha1_fingerprint": "",
        "cert_format": "X.509",
        "cert_extension": ".crt",
        "san": [],
        "is_expired": False,
        "days_until_expiry": 0,
    }


def _get_key_size(pub_key) -> int:
    if hasattr(pub_key, 'key_size'):
        return pub_key.key_size
    if hasattr(pub_key, 'curve'):
        # EC key — return curve size
        curve_name = pub_key.curve.name
        if "521" in curve_name: return 521
        if "384" in curve_name: return 384
        if "256" in curve_name: return 256
        if "224" in curve_name: return 224
        return 256
    return 0


def _get_key_type(pub_key) -> str:
    if isinstance(pub_key, rsa.RSAPublicKey):
        return "RSA"
    if isinstance(pub_key, ec.EllipticCurvePublicKey):
        return "EC"
    if isinstance(pub_key, dsa.DSAPublicKey):
        return "DSA"
    return "Unknown"


def _get_san(cert: x509.Certificate) -> list:
    try:
        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        return [str(name.value) for name in san_ext.value]
    except Exception:
        return []
