"""
Report Generator — Generates executive, scheduled, and on-demand reports
in PDF format with QuantumSight / PNB branding and full CBOM data.
"""
import io
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, PageBreak
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

PNB_RED = colors.HexColor("#8B0000") if REPORTLAB_AVAILABLE else None
PNB_GOLD = colors.HexColor("#F59E0B") if REPORTLAB_AVAILABLE else None
PNB_DARK = colors.HexColor("#1A1A2E") if REPORTLAB_AVAILABLE else None
PNB_GREEN = colors.HexColor("#16A34A") if REPORTLAB_AVAILABLE else None


def generate_executive_report(
    summary: dict,
    assets: list,
    cbom_entries: list,
    ratings: list,
    hndl_risks: list
) -> bytes:
    """Generate a full executive PDF report."""
    if not REPORTLAB_AVAILABLE:
        return b"%PDF-1.4 PLACEHOLDER"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title="QuantumSight Executive Report",
        author="QuantumSight — PNB Cybersecurity",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Title Page ─────────────────────────────────────────────────────────
    _add_title_page(story, styles, summary)
    story.append(PageBreak())

    # ── Executive Summary ──────────────────────────────────────────────────
    _add_section_header(story, styles, "1. Executive Summary")
    _add_executive_summary(story, styles, summary)
    story.append(Spacer(1, 0.5*cm))

    # ── Enterprise Rating ──────────────────────────────────────────────────
    _add_section_header(story, styles, "2. Enterprise PQC Cyber Rating")
    _add_rating_summary(story, styles, summary, ratings)
    story.append(Spacer(1, 0.5*cm))

    # ── Asset Inventory Table ──────────────────────────────────────────────
    _add_section_header(story, styles, "3. Asset Inventory")
    _add_asset_table(story, styles, assets)
    story.append(Spacer(1, 0.5*cm))

    # ── HNDL Risk Summary ─────────────────────────────────────────────────
    _add_section_header(story, styles, "4. HNDL Risk Assessment")
    _add_hndl_table(story, styles, hndl_risks, assets)
    story.append(Spacer(1, 0.5*cm))

    # ── CBOM Summary ──────────────────────────────────────────────────────
    _add_section_header(story, styles, "5. Cryptographic Bill of Materials (CBOM)")
    _add_cbom_summary(story, styles, cbom_entries)

    # ── Recommendations ───────────────────────────────────────────────────
    story.append(PageBreak())
    _add_section_header(story, styles, "6. Recommendations")
    _add_recommendations(story, styles, summary, ratings)

    doc.build(story)
    return buffer.getvalue()


def _add_title_page(story, styles, summary):
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        textColor=PNB_RED,
        fontSize=28,
        spaceAfter=12
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        textColor=PNB_DARK,
        fontSize=14,
        alignment=TA_CENTER
    )
    story.append(Spacer(1, 3*cm))
    story.append(Paragraph("QuantumSight", title_style))
    story.append(Paragraph("AI-Augmented Cryptographic Intelligence Platform", subtitle_style))
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=PNB_GOLD))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "<b>Executive Report — Post-Quantum Cryptographic Posture Assessment</b>",
        ParagraphStyle("SubH", parent=styles["Normal"], fontSize=16, alignment=TA_CENTER, textColor=PNB_DARK)
    ))
    story.append(Spacer(1, 1*cm))

    meta_data = [
        ["Report Type:", "Executive Summary"],
        ["Organization:", "Punjab National Bank (PNB)"],
        ["Generated:", datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")],
        ["Classification:", "CONFIDENTIAL"],
        ["Platform:", "QuantumSight v1.0 | Team Incognito"],
        ["Standard:", "CERT-IN Annexure-A | NIST FIPS 203/204/205"],
        ["Total Assets Scanned:", str(summary.get("total_assets", 0))],
        ["Enterprise Score:", f"{summary.get('enterprise_score', 0)}/1000 — {summary.get('enterprise_tier', 'Standard')}"],
    ]

    t = Table(meta_data, colWidths=[5*cm, 10*cm])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), PNB_RED),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)


def _add_section_header(story, styles, title: str):
    style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading1"],
        textColor=PNB_RED,
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
    )
    story.append(Paragraph(title, style))
    story.append(HRFlowable(width="100%", thickness=1, color=PNB_GOLD))
    story.append(Spacer(1, 0.3*cm))


def _add_executive_summary(story, styles, summary):
    normal = styles["Normal"]
    total = summary.get("total_assets", 0)
    critical = summary.get("assets_by_tier", {}).get("Critical", 0)
    pqc_ready = summary.get("pqc_ready_count", 0)
    score = summary.get("enterprise_score", 0)

    text = (
        f"QuantumSight conducted a comprehensive Post-Quantum Cryptographic assessment of "
        f"<b>{total} public-facing assets</b> belonging to Punjab National Bank. "
        f"The enterprise PQC Cyber Rating is <b>{score}/1000</b> ({summary.get('enterprise_tier', 'Standard')} tier). "
        f"<b>{pqc_ready} assets</b> have achieved Elite-PQC status (quantum-safe). "
        f"<b>{critical} assets</b> require immediate attention due to critical cryptographic vulnerabilities. "
        "<br/><br/>"
        "The primary threat addressed is <b>Harvest Now, Decrypt Later (HNDL)</b>: adversaries are "
        "intercepting and storing PNB's encrypted banking traffic TODAY, intending to decrypt it "
        "once Cryptographically Relevant Quantum Computers (CRQCs) become available (estimated 2030–2035). "
        "Non-PQC assets face a direct quantum decryption risk window."
    )
    story.append(Paragraph(text, normal))


def _add_rating_summary(story, styles, summary, ratings):
    dist = summary.get("assets_by_tier", {})
    table_data = [
        ["Tier", "Score Range", "Count", "Action Required"],
        ["Critical", "0–399", str(dist.get("Critical", 0)), "Immediate isolation & replacement"],
        ["Legacy", "400–699", str(dist.get("Legacy", 0)), "Replace within 6 months"],
        ["Standard", "700–849", str(dist.get("Standard", 0)), "Migrate to PQC within 12-24 months"],
        ["Elite-PQC", "850–1000", str(dist.get("Elite-PQC", 0)), "Issue PQC-Ready Certificate"],
    ]
    t = Table(table_data, colWidths=[3.5*cm, 3*cm, 2*cm, 8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PNB_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TEXTCOLOR', (0, 1), (0, 1), colors.red),
        ('TEXTCOLOR', (0, 2), (0, 2), colors.HexColor("#EA580C")),
        ('TEXTCOLOR', (0, 3), (0, 3), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 4), (0, 4), PNB_GREEN),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)


def _add_asset_table(story, styles, assets):
    if not assets:
        story.append(Paragraph("No assets found.", styles["Normal"]))
        return

    headers = ["Hostname", "Type", "TLS", "Cipher (truncated)", "Score", "Tier"]
    rows = [headers]
    for a in assets[:20]:  # Limit to 20 in report
        rows.append([
            str(a.get("hostname", ""))[:30],
            str(a.get("asset_type", "")),
            str(a.get("tls_version", "")),
            str(a.get("cipher_suite", ""))[:25],
            str(a.get("total_score", "")),
            str(a.get("tier", "")),
        ])

    t = Table(rows, colWidths=[4.5*cm, 2.5*cm, 2*cm, 3.5*cm, 1.5*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PNB_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)


def _add_hndl_table(story, styles, hndl_risks, assets):
    asset_map = {a.get("id", ""): a.get("hostname", "") for a in assets}

    if not hndl_risks:
        story.append(Paragraph("No HNDL risk assessments available.", styles["Normal"]))
        return

    headers = ["Asset", "Risk Level", "Breach Year", "Years Left", "Urgency"]
    rows = [headers]
    for h in hndl_risks[:15]:
        hostname = asset_map.get(h.get("asset_id", ""), h.get("hostname", "Unknown"))
        rows.append([
            str(hostname)[:28],
            str(h.get("hndl_risk_level", "")),
            str(h.get("estimated_breach_year", "N/A")),
            str(h.get("years_until_threat", "N/A")),
            str(h.get("urgency", ""))[:40],
        ])

    t = Table(rows, colWidths=[4.5*cm, 2.5*cm, 2.5*cm, 2*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PNB_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)


def _add_cbom_summary(story, styles, cbom_entries):
    total = len(cbom_entries)
    story.append(Paragraph(
        f"Total CBOM entries: <b>{total}</b> assets mapped per CERT-IN Annexure-A specification.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.3*cm))

    if not cbom_entries:
        return

    headers = ["Hostname", "Cipher", "Key Size", "TLS Version", "Cert State"]
    rows = [headers]
    for e in cbom_entries[:15]:
        rows.append([
            str(e.get("cert_name", e.get("hostname", "")))[:28],
            str(e.get("algo_name", ""))[:30],
            str(e.get("key_size", "")),
            str(e.get("protocol_version", "")),
            str(e.get("key_state", "")),
        ])

    t = Table(rows, colWidths=[5*cm, 4*cm, 2*cm, 3*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PNB_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)


def _add_recommendations(story, styles, summary, ratings):
    recs = [
        ("1. Immediate — Isolate Critical Assets",
         "Assets scoring 0–399 (Critical tier) must be isolated from public internet access "
         "immediately. These include SSLv3 endpoints and RC4/DES cipher suites that represent "
         "both classical and quantum decryption risks."),
        ("2. High Priority — Legacy Protocol Replacement",
         "All TLS 1.0/1.1 endpoints must be migrated to TLS 1.2 minimum (TLS 1.3 preferred) "
         "within 6 months. Configure HSTS, disable CBC cipher suites, enable AEAD-only ciphers."),
        ("3. Medium — Begin PQC Migration Planning",
         "Initiate NIST PQC migration programme for Standard-tier assets. Adopt ML-KEM-768 "
         "(FIPS 203) for key encapsulation and ML-DSA-65 (FIPS 204) for digital signatures. "
         "Deploy hybrid classical+PQC mode for zero-downtime migration."),
        ("4. Ongoing — CBOM Maintenance",
         "Maintain the Cryptographic Bill of Materials in QuantumSight with quarterly scan "
         "updates. Ensure all CERT-IN Annexure-A fields are populated for every new asset "
         "deployed in PNB's public-facing infrastructure."),
        ("5. Certificate Renewals",
         "Renew all certificates expiring within 90 days. Prioritize renewal with PQC-capable "
         "Certificate Authorities (DigiCert FIPS 205 pilot, Entrust PQC PKI) when available."),
    ]

    for title, body in recs:
        story.append(Paragraph(
            f"<b>{title}</b>",
            ParagraphStyle("RecTitle", parent=styles["Normal"], textColor=PNB_RED, fontSize=11)
        ))
        story.append(Paragraph(body, styles["Normal"]))
        story.append(Spacer(1, 0.3*cm))
