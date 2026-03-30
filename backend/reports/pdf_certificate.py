"""
PDF Certificate Generator — Issues PQC-Ready digital certificates for
assets that have achieved Elite-PQC status. Generates professional
PDF certificates with PNB branding, NIST algorithm details, and
scan timestamp provenance.
"""
import io
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab not installed — PDF generation disabled")


# PNB Brand Colors
PNB_RED = colors.HexColor("#8B0000")
PNB_GOLD = colors.HexColor("#B8860B")
PNB_LIGHT_GOLD = colors.HexColor("#F59E0B")
PNB_DARK = colors.HexColor("#1A1A2E")
PNB_GREEN = colors.HexColor("#16A34A")
PNB_GRAY = colors.HexColor("#6B7280")
PNB_LIGHT_GRAY = colors.HexColor("#F3F4F6")


def generate_pqc_certificate(asset_data: dict, scan_data: dict, pqc_data: dict, rating_data: dict) -> bytes:
    """
    Generate a PDF PQC-Ready certificate for a compliant asset.
    Returns PDF as bytes.
    """
    if not REPORTLAB_AVAILABLE:
        return _dummy_pdf(asset_data)

    buffer = io.BytesIO()

    # Use canvas for full control
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4  # 595.27, 841.89 points

    _draw_certificate(c, width, height, asset_data, scan_data, pqc_data, rating_data)

    c.save()
    return buffer.getvalue()


def _draw_certificate(c, width, height, asset_data, scan_data, pqc_data, rating_data):
    """Draw the full certificate page."""
    # ── Background ──────────────────────────────────────────────────────────
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer border (double border effect)
    c.setStrokeColor(PNB_RED)
    c.setLineWidth(4)
    c.rect(15, 15, width - 30, height - 30, fill=0, stroke=1)
    c.setStrokeColor(PNB_GOLD)
    c.setLineWidth(1.5)
    c.rect(22, 22, width - 44, height - 44, fill=0, stroke=1)

    # ── Header Band ──────────────────────────────────────────────────────────
    c.setFillColor(PNB_RED)
    c.rect(22, height - 130, width - 44, 108, fill=1, stroke=0)

    # PNB Logo Text
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 42)
    c.drawCentredString(width / 2, height - 75, "pnb")

    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 95, "PUNJAB NATIONAL BANK")

    c.setFillColor(PNB_LIGHT_GOLD)
    c.setFont("Helvetica", 9)
    c.drawCentredString(width / 2, height - 112, "India's Second Largest Public Sector Bank")

    # ── Certificate Title ────────────────────────────────────────────────────
    c.setFillColor(PNB_DARK)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(width / 2, height - 175, "CERTIFICATE OF")

    c.setFillColor(PNB_RED)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 210, "POST-QUANTUM CRYPTOGRAPHIC")
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 242, "READINESS")

    # Gold underline
    c.setStrokeColor(PNB_GOLD)
    c.setLineWidth(2)
    c.line(80, height - 252, width - 80, height - 252)

    # ── Subtitle ─────────────────────────────────────────────────────────────
    c.setFillColor(PNB_GRAY)
    c.setFont("Helvetica", 11)
    c.drawCentredString(
        width / 2, height - 275,
        "Issued by QuantumSight — AI-Augmented Cryptographic Intelligence Platform"
    )
    c.drawCentredString(
        width / 2, height - 290,
        "In collaboration with IIT Kanpur | PNB Cybersecurity Hackathon 2026"
    )

    # ── Green "CERTIFIED" Badge ───────────────────────────────────────────────
    badge_y = height - 355
    c.setFillColor(PNB_GREEN)
    c.roundRect(width / 2 - 90, badge_y, 180, 40, 20, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, badge_y + 14, "✓  ELITE-PQC CERTIFIED")

    # ── Main Content Area ────────────────────────────────────────────────────
    hostname = asset_data.get("hostname", "Unknown Asset")
    score = rating_data.get("total_score", 0)
    fips = pqc_data.get("fips_standard", "FIPS 203/204")
    algo = (pqc_data.get("recommended_replacement") or {}).get("algorithm", "ML-KEM-768")
    issuer = scan_data.get("issuer", "Unknown CA")
    scan_time = scan_data.get("scan_time", datetime.utcnow().isoformat())

    # Issued to section
    c.setFillColor(PNB_DARK)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 415, "This certificate is issued to:")

    c.setFillColor(PNB_RED)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 440, hostname)

    # Score display
    c.setFillColor(PNB_DARK)
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 462, f"PQC Cyber Rating: {score}/1000 — Elite-PQC Tier")

    # ── Details Table ─────────────────────────────────────────────────────────
    table_y = height - 555
    row_h = 22
    col1_x = 80
    col2_x = 300

    details = [
        ("Asset Type", asset_data.get("asset_type", "Web Application")),
        ("TLS Version", scan_data.get("tls_version", "TLS 1.3")),
        ("Cipher Suite", (scan_data.get("cipher_suite", "") or "")[:50]),
        ("Key Size", f"{scan_data.get('cert_key_size', 0)} bits"),
        ("NIST Standard", fips),
        ("Certificate Authority", _extract_ca_name(issuer)),
        ("Certificate Status", "Valid — Quantum-Safe"),
        ("Scan Timestamp", _format_date(scan_time)),
        ("Valid Until", _format_date(
            (datetime.utcnow() + timedelta(days=365)).isoformat()
        )),
    ]

    # Table header
    c.setFillColor(PNB_DARK)
    c.rect(col1_x - 10, table_y + row_h * len(details) + 5,
           width - 2 * col1_x + 20, 22, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(col1_x, table_y + row_h * len(details) + 10, "ASSET DETAILS")
    c.drawString(col2_x, table_y + row_h * len(details) + 10, "VALUE")

    # Table rows
    for i, (label, value) in enumerate(details):
        y = table_y + (len(details) - 1 - i) * row_h
        # Alternating background
        if i % 2 == 0:
            c.setFillColor(PNB_LIGHT_GRAY)
            c.rect(col1_x - 10, y, width - 2 * col1_x + 20, row_h, fill=1, stroke=0)

        c.setFillColor(PNB_DARK)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(col1_x, y + 7, label)
        c.setFont("Helvetica", 9)
        c.drawString(col2_x, y + 7, str(value))

    # Table border
    c.setStrokeColor(PNB_GRAY)
    c.setLineWidth(0.5)
    c.rect(col1_x - 10, table_y,
           width - 2 * col1_x + 20,
           row_h * len(details) + 22, fill=0, stroke=1)

    # ── HNDL Status Box ──────────────────────────────────────────────────────
    hndl_y = table_y - 60
    c.setFillColor(colors.HexColor("#DCFCE7"))  # Light green
    c.roundRect(col1_x - 10, hndl_y, width - 2 * col1_x + 20, 45, 5, fill=1, stroke=0)
    c.setStrokeColor(PNB_GREEN)
    c.setLineWidth(1)
    c.roundRect(col1_x - 10, hndl_y, width - 2 * col1_x + 20, 45, 5, fill=0, stroke=1)

    c.setFillColor(PNB_GREEN)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, hndl_y + 28, "HNDL RISK: MITIGATED")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#166534"))
    c.drawCentredString(
        width / 2, hndl_y + 12,
        "This asset's encrypted traffic is SAFE from Harvest Now, Decrypt Later attacks."
    )

    # ── Compliance Badges ─────────────────────────────────────────────────────
    badges_y = hndl_y - 50
    badge_w = 110
    badge_h = 30
    badge_spacing = 15
    total_w = 3 * badge_w + 2 * badge_spacing
    start_x = (width - total_w) / 2

    badge_data = [
        ("NIST FIPS 203", "ML-KEM"),
        ("NIST FIPS 204", "ML-DSA"),
        ("CERT-IN CBOM", "Annexure-A"),
    ]
    for i, (title, sub) in enumerate(badge_data):
        bx = start_x + i * (badge_w + badge_spacing)
        c.setFillColor(PNB_DARK)
        c.roundRect(bx, badges_y, badge_w, badge_h, 4, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(bx + badge_w / 2, badges_y + 18, title)
        c.setFillColor(PNB_LIGHT_GOLD)
        c.setFont("Helvetica", 7)
        c.drawCentredString(bx + badge_w / 2, badges_y + 7, sub)

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFillColor(PNB_RED)
    c.rect(22, 22, width - 44, 55, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(
        width / 2, 58,
        "QuantumSight — PNB Cybersecurity Hackathon 2026 | Team Incognito | Thapar Institute of Engineering & Technology"
    )
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        width / 2, 44,
        f"Certificate ID: QS-{asset_data.get('id', 'DEMO')[:8].upper()} | "
        f"Issued: {_format_date(datetime.utcnow().isoformat())} | "
        "Verify at: quantumsight.pnb.bank.in"
    )
    c.setFillColor(PNB_LIGHT_GOLD)
    c.setFont("Helvetica", 7)
    c.drawCentredString(
        width / 2, 30,
        "This certificate attests that the named asset implements NIST-standardized Post-Quantum Cryptography and is protected against HNDL attacks."
    )

    c.showPage()


def _format_date(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d %B %Y, %H:%M UTC")
    except Exception:
        return iso_str[:19] if iso_str else "N/A"


def _extract_ca_name(issuer_dn: str) -> str:
    if not issuer_dn:
        return "Unknown CA"
    from utils.helpers import extract_issuer_org
    return extract_issuer_org(issuer_dn)


def _dummy_pdf(asset_data: dict) -> bytes:
    """Return minimal PDF when reportlab is unavailable."""
    content = f"%PDF-1.4\n1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    return content.encode()
