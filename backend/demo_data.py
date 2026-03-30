"""
Demo Data Seeder — Seeds the database with realistic PNB-like assets
for demonstration purposes. Provides a live, impressive dashboard even
before any real scans are initiated.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from database.supabase_client import insert_record, get_records
from scanner.asset_classifier import classify_asset
from cbom.cbom_builder import build_cbom_entry
from intelligence.pqc_validator import validate_pqc
from intelligence.hndl_engine import calculate_hndl_risk
from intelligence.cyber_rating import calculate_cyber_rating


# Realistic PNB-like asset scenarios with varied crypto postures
DEMO_ASSETS = [
    {
        "hostname": "portal.pnb.bank.in",
        "ip": "34.12.11.45",
        "type": "Web App",
        "cipher": "ECDHE-RSA-AES256-GCM-SHA384",
        "tls": "TLS 1.2",
        "key_size": 2048,
        "key_type": "RSA",
        "issuer": "C=US,O=DigiCert Inc,CN=DigiCert SHA2 Secure Server CA",
        "days_valid": 180,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "api.pnb.bank.in",
        "ip": "34.12.11.90",
        "ipv6": "2001:db8::90",
        "type": "API",
        "cipher": "TLS_AES_256_GCM_SHA384",
        "tls": "TLS 1.3",
        "key_size": 4096,
        "key_type": "RSA",
        "issuer": "C=US,O=Let's Encrypt,CN=R3",
        "days_valid": 85,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "vpn.pnb.bank.in",
        "ip": "34.55.90.21",
        "type": "Gateway",
        "cipher": "TLS_RSA_WITH_DES_CBC_SHA",
        "tls": "TLS 1.0",
        "key_size": 1024,
        "key_type": "RSA",
        "issuer": "C=GB,O=COMODO CA Limited,CN=COMODO RSA Domain Validation Secure Server CA",
        "days_valid": 12,
        "sig_algo": "sha1",
        "sig_oid": "1.2.840.113549.1.1.5",
    },
    {
        "hostname": "mail.pnb.bank.in",
        "ip": "35.11.44.10",
        "type": "Mail Server",
        "cipher": "ECDHE-ECDSA-AES256-GCM-SHA384",
        "tls": "TLS 1.2",
        "key_size": 3072,
        "key_type": "RSA",
        "issuer": "C=BE,O=GlobalSign nv-sa,CN=GlobalSign RSA OV SSL CA 2018",
        "days_valid": 290,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "netbanking.pnb.bank.in",
        "ip": "34.77.21.12",
        "type": "Web App",
        "cipher": "ECDHE-RSA-AES128-GCM-SHA256",
        "tls": "TLS 1.2",
        "key_size": 2048,
        "key_type": "RSA",
        "issuer": "C=US,O=DigiCert Inc,CN=DigiCert SHA2 Secure Server CA",
        "days_valid": 45,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "mobileapi.pnb.bank.in",
        "ip": "34.88.32.15",
        "ipv6": "2001:db8::15",
        "type": "API",
        "cipher": "TLS_AES_128_GCM_SHA256",
        "tls": "TLS 1.3",
        "key_size": 2048,
        "key_type": "RSA",
        "issuer": "C=US,O=Let's Encrypt,CN=R3",
        "days_valid": 62,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "payments.pnb.bank.in",
        "ip": "34.99.10.5",
        "type": "API",
        "cipher": "ECDHE-RSA-AES256-GCM-SHA384",
        "tls": "TLS 1.2",
        "key_size": 4096,
        "key_type": "RSA",
        "issuer": "C=US,O=DigiCert Inc,CN=DigiCert SHA2 Extended Validation Server CA",
        "days_valid": 220,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "legacy.pnb.bank.in",
        "ip": "34.100.5.2",
        "type": "Web App",
        "cipher": "RC4-MD5",
        "tls": "SSLv3",
        "key_size": 512,
        "key_type": "RSA",
        "issuer": "C=US,O=Symantec Corporation,CN=Symantec Class 3 Secure Server CA - G4",
        "days_valid": -30,  # Expired
        "sig_algo": "md5",
        "sig_oid": "1.2.840.113549.1.1.4",
    },
    {
        "hostname": "atm.pnb.bank.in",
        "ip": "34.101.15.3",
        "type": "API",
        "cipher": "ECDHE-RSA-CHACHA20-POLY1305",
        "tls": "TLS 1.3",
        "key_size": 256,
        "key_type": "EC",
        "issuer": "C=US,O=DigiCert Inc,CN=DigiCert TLS RSA SHA256 2020 CA1",
        "days_valid": 310,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "auth.pnb.bank.in",
        "ip": "34.102.20.8",
        "type": "Auth/SSO",
        "cipher": "ECDHE-ECDSA-CHACHA20-POLY1305",
        "tls": "TLS 1.3",
        "key_size": 384,
        "key_type": "EC",
        "issuer": "C=US,O=Entrust,CN=Entrust Certification Authority - L1K",
        "days_valid": 185,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "cdn.pnb.bank.in",
        "ip": "34.103.5.99",
        "type": "CDN/Static",
        "cipher": "TLS_AES_256_GCM_SHA384",
        "tls": "TLS 1.3",
        "key_size": 2048,
        "key_type": "RSA",
        "issuer": "C=US,O=Let's Encrypt,CN=R3",
        "days_valid": 55,
        "sig_algo": "sha256",
        "sig_oid": "1.2.840.113549.1.1.11",
    },
    {
        "hostname": "reporting.pnb.bank.in",
        "ip": "34.104.10.77",
        "type": "Web App",
        "cipher": "AES256-SHA",
        "tls": "TLS 1.1",
        "key_size": 2048,
        "key_type": "RSA",
        "issuer": "C=US,O=Thawte Inc,CN=Thawte RSA CA 2018",
        "days_valid": 95,
        "sig_algo": "sha1",
        "sig_oid": "1.2.840.113549.1.1.5",
    },
]


def _build_scan_data(demo: dict, now: datetime) -> dict:
    """Build a realistic scan_data dict from demo spec."""
    days_valid = demo.get("days_valid", 180)
    not_before = (now - timedelta(days=365 - days_valid)).isoformat()
    not_after = (now + timedelta(days=max(days_valid, 0))).isoformat()
    is_expired = days_valid < 0
    actual_days = max(days_valid, 0)

    return {
        "hostname": demo["hostname"],
        "port": 443,
        "scan_time": now.isoformat(),
        "tls_version": demo["tls"],
        "cipher_suite": demo["cipher"],
        "key_bits": demo["key_size"],
        "cert_key_size": demo["key_size"],
        "cert_key_type": demo.get("key_type", "RSA"),
        "signature_algorithm": demo.get("sig_algo", "sha256"),
        "signature_algorithm_oid": demo.get("sig_oid", "1.2.840.113549.1.1.11"),
        "subject": f"CN={demo['hostname']},O=Punjab National Bank,C=IN",
        "issuer": demo.get("issuer", "C=US,O=DigiCert Inc,CN=DigiCert Root"),
        "not_valid_before": not_before,
        "not_valid_after": not_after,
        "serial_number": str(abs(hash(demo["hostname"]))),
        "sha256_fingerprint": f"{abs(hash(demo['hostname'] + 'sha256')):064x}",
        "sha1_fingerprint": f"{abs(hash(demo['hostname'] + 'sha1')):040x}",
        "cert_format": "X.509",
        "cert_extension": ".crt",
        "san": [demo["hostname"], f"www.{demo['hostname']}"],
        "is_expired": is_expired,
        "days_until_expiry": actual_days,
        "scan_success": True,
        "error": None,
    }


def seed_demo_data() -> dict:
    """
    Seed the database with demo assets and compute all intelligence scores.
    Returns summary of seeded data.
    """
    # Check if already seeded
    existing = get_records("assets", limit=5)
    if existing:
        return {"seeded": False, "message": "Demo data already exists", "count": len(existing)}

    now = datetime.now(timezone.utc)
    seeded_count = 0
    session_id = str(uuid.uuid4())

    # Create scan session
    session_record = {
        "id": session_id,
        "target_domains": [d["hostname"] for d in DEMO_ASSETS],
        "status": "completed",
        "total_assets": len(DEMO_ASSETS),
        "scanned_assets": len(DEMO_ASSETS),
        "started_at": (now - timedelta(minutes=5)).isoformat(),
        "completed_at": now.isoformat(),
    }
    insert_record("scan_sessions", session_record)

    for demo in DEMO_ASSETS:
        asset_id = str(uuid.uuid4())
        scan_data = _build_scan_data(demo, now)

        # Classify asset
        classification = classify_asset(demo["hostname"])

        # Build all intelligence scores
        pqc_data = validate_pqc(scan_data)
        hndl_data = calculate_hndl_risk(scan_data, pqc_data)
        rating_data = calculate_cyber_rating(scan_data, pqc_data, hndl_data)
        cbom_entry = build_cbom_entry(scan_data)

        # Asset record
        asset_record = {
            "id": asset_id,
            "hostname": demo["hostname"],
            "url": f"https://{demo['hostname']}",
            "ip_address": demo.get("ip"),
            "ipv6_address": demo.get("ipv6"),
            "asset_type": demo["type"],
            "owner": classification["owner"],
            "ports": [443, 80],
            "scan_session_id": session_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        insert_record("assets", asset_record)

        # Scan result
        scan_record = {
            "id": str(uuid.uuid4()),
            "asset_id": asset_id,
            "tls_version": scan_data["tls_version"],
            "cipher_suite": scan_data["cipher_suite"],
            "key_bits": scan_data["key_bits"],
            "cert_key_size": scan_data["cert_key_size"],
            "cert_key_type": scan_data["cert_key_type"],
            "signature_algorithm": scan_data["signature_algorithm"],
            "signature_algorithm_oid": scan_data["signature_algorithm_oid"],
            "subject": scan_data["subject"],
            "issuer": scan_data["issuer"],
            "not_valid_before": scan_data["not_valid_before"],
            "not_valid_after": scan_data["not_valid_after"],
            "serial_number": scan_data["serial_number"],
            "sha256_fingerprint": scan_data["sha256_fingerprint"],
            "san": scan_data["san"],
            "is_expired": scan_data["is_expired"],
            "days_until_expiry": scan_data["days_until_expiry"],
            "scan_success": True,
            "scanned_at": now.isoformat(),
        }
        insert_record("scan_results", scan_record)

        # CBOM entry
        cbom_record = {**cbom_entry, "id": str(uuid.uuid4()), "asset_id": asset_id}
        insert_record("cbom_entries", cbom_record)

        # PQC score
        pqc_record = {**pqc_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": demo["hostname"]}
        insert_record("pqc_scores", pqc_record)

        # HNDL risk
        hndl_record = {**hndl_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": demo["hostname"]}
        insert_record("hndl_risk", hndl_record)

        # Cyber rating
        rating_record = {**rating_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": demo["hostname"]}
        insert_record("cyber_ratings", rating_record)

        seeded_count += 1

    return {
        "seeded": True,
        "message": f"Seeded {seeded_count} demo assets",
        "count": seeded_count,
        "session_id": session_id
    }
