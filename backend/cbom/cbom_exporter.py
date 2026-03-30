"""
CBOM Exporter — Exports CBOM data in JSON, CSV, XML, and PDF formats.
Supports all CERT-IN Annexure-A required export formats for regulatory
compliance reporting.
"""
import json
import csv
import io
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def export_json(cbom_entries: list) -> str:
    """Export CBOM as formatted JSON."""
    payload = {
        "cbom_version": "1.0",
        "standard": "CERT-IN Annexure-A",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_entries": len(cbom_entries),
        "entries": cbom_entries
    }
    return json.dumps(payload, indent=2, default=str)


def export_csv(cbom_entries: list) -> str:
    """Export CBOM as CSV with all Annexure-A column headers."""
    if not cbom_entries:
        return ""

    output = io.StringIO()
    fieldnames = [
        "hostname", "algo_name", "algo_asset_type", "algo_primitive",
        "algo_mode", "algo_crypto_functions", "algo_classical_security_level",
        "algo_oid", "key_name", "key_asset_type", "key_id", "key_state",
        "key_size", "key_creation_date", "key_activation_date",
        "protocol_name", "protocol_asset_type", "protocol_version",
        "protocol_cipher_suites", "protocol_oid",
        "cert_name", "cert_asset_type", "cert_subject_name", "cert_issuer_name",
        "cert_not_valid_before", "cert_not_valid_after",
        "cert_signature_algorithm_ref", "cert_subject_public_key_ref",
        "cert_format", "cert_extension", "cert_sha256_fingerprint",
        "days_until_expiry", "is_expired"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()

    for entry in cbom_entries:
        row = {k: v for k, v in entry.items() if k in fieldnames}
        # Flatten lists
        if isinstance(row.get("algo_crypto_functions"), list):
            row["algo_crypto_functions"] = "|".join(row["algo_crypto_functions"])
        writer.writerow(row)

    return output.getvalue()


def export_xml(cbom_entries: list) -> str:
    """Export CBOM as XML with all Annexure-A elements."""
    root = ET.Element("CBOM")
    root.set("version", "1.0")
    root.set("standard", "CERT-IN Annexure-A")
    root.set("generated_at", datetime.utcnow().isoformat() + "Z")
    root.set("total_entries", str(len(cbom_entries)))

    for entry in cbom_entries:
        asset_el = ET.SubElement(root, "Asset")
        asset_el.set("hostname", str(entry.get("hostname", "")))

        # Algorithm section
        algo_el = ET.SubElement(asset_el, "Algorithm")
        _add_xml_child(algo_el, "Name", entry.get("algo_name"))
        _add_xml_child(algo_el, "AssetType", entry.get("algo_asset_type"))
        _add_xml_child(algo_el, "Primitive", entry.get("algo_primitive"))
        _add_xml_child(algo_el, "Mode", entry.get("algo_mode"))
        _add_xml_child(algo_el, "CryptoFunctions",
                       "|".join(entry.get("algo_crypto_functions") or []))
        _add_xml_child(algo_el, "ClassicalSecurityLevel",
                       str(entry.get("algo_classical_security_level", "")))
        _add_xml_child(algo_el, "OID", entry.get("algo_oid"))

        # Key section
        key_el = ET.SubElement(asset_el, "Key")
        _add_xml_child(key_el, "Name", entry.get("key_name"))
        _add_xml_child(key_el, "AssetType", entry.get("key_asset_type"))
        _add_xml_child(key_el, "ID", entry.get("key_id"))
        _add_xml_child(key_el, "State", entry.get("key_state"))
        _add_xml_child(key_el, "Size", str(entry.get("key_size", "")))
        _add_xml_child(key_el, "CreationDate", str(entry.get("key_creation_date", "")))
        _add_xml_child(key_el, "ActivationDate", str(entry.get("key_activation_date", "")))

        # Protocol section
        proto_el = ET.SubElement(asset_el, "Protocol")
        _add_xml_child(proto_el, "Name", entry.get("protocol_name"))
        _add_xml_child(proto_el, "AssetType", entry.get("protocol_asset_type"))
        _add_xml_child(proto_el, "Version", entry.get("protocol_version"))
        _add_xml_child(proto_el, "CipherSuites", entry.get("protocol_cipher_suites"))
        _add_xml_child(proto_el, "OID", entry.get("protocol_oid"))

        # Certificate section
        cert_el = ET.SubElement(asset_el, "Certificate")
        _add_xml_child(cert_el, "Name", entry.get("cert_name"))
        _add_xml_child(cert_el, "AssetType", entry.get("cert_asset_type"))
        _add_xml_child(cert_el, "SubjectName", entry.get("cert_subject_name"))
        _add_xml_child(cert_el, "IssuerName", entry.get("cert_issuer_name"))
        _add_xml_child(cert_el, "NotValidBefore", str(entry.get("cert_not_valid_before", "")))
        _add_xml_child(cert_el, "NotValidAfter", str(entry.get("cert_not_valid_after", "")))
        _add_xml_child(cert_el, "SignatureAlgorithmRef", entry.get("cert_signature_algorithm_ref"))
        _add_xml_child(cert_el, "SubjectPublicKeyRef", entry.get("cert_subject_public_key_ref"))
        _add_xml_child(cert_el, "Format", entry.get("cert_format"))
        _add_xml_child(cert_el, "Extension", entry.get("cert_extension"))
        _add_xml_child(cert_el, "SHA256Fingerprint", entry.get("cert_sha256_fingerprint"))

    # Pretty print
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def _add_xml_child(parent: ET.Element, tag: str, text: str) -> None:
    child = ET.SubElement(parent, tag)
    child.text = str(text) if text is not None else ""
