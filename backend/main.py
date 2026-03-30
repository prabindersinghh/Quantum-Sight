"""
QuantumSight — FastAPI Backend
AI-Augmented Cryptographic Intelligence Platform for PNB Cybersecurity Hackathon 2026.
Team Incognito | Thapar Institute of Engineering & Technology, Patiala.
"""
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io

# Internal modules
from scanner.tls_scanner import scan_domain
from scanner.domain_discovery import discover_domains
from scanner.port_scanner import scan_ports
from scanner.asset_classifier import classify_asset
from cbom.cbom_builder import build_cbom_entry
from cbom.cbom_exporter import export_json, export_csv, export_xml
from intelligence.pqc_validator import validate_pqc
from intelligence.hndl_engine import calculate_hndl_risk
from intelligence.cyber_rating import calculate_cyber_rating, calculate_enterprise_rating
from intelligence.ai_copilot import generate_migration_plan
from reports.pdf_certificate import generate_pqc_certificate
from reports.report_generator import generate_executive_report
from database.supabase_client import (
    insert_record, upsert_record, get_records, get_record_by_id,
    log_audit_event, is_memory_mode
)
from database.models import (
    ScanRequest, MigrationPlanRequest, OnDemandReportRequest,
    ScheduledReportRequest
)
from utils.helpers import (
    success_response, error_response, clean_hostname, is_valid_hostname,
    utc_now
)
from demo_data import seed_demo_data

# ── App setup ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="QuantumSight API",
    description="AI-Augmented Cryptographic Intelligence Platform — PNB Hackathon 2026",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — allow React frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections for scan progress
_ws_connections: dict = {}
# Active scan sessions
_scan_sessions: dict = {}


# ── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    logger.info("QuantumSight API starting up...")
    logger.info(f"Database mode: {'Memory (demo)' if is_memory_mode() else 'Supabase'}")
    # Seed demo data on startup
    result = seed_demo_data()
    logger.info(f"Demo data: {result['message']}")


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return success_response(
        data={
            "status": "healthy",
            "version": "1.0.0",
            "db_mode": "memory" if is_memory_mode() else "supabase",
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY", ""))
        },
        message="QuantumSight API is running"
    )


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/api/dashboard/summary")
async def dashboard_summary():
    """Returns all metrics needed for the home dashboard."""
    assets = get_records("assets")
    scan_results = get_records("scan_results")
    pqc_scores = get_records("pqc_scores")
    hndl_risks = get_records("hndl_risk")
    cyber_ratings = get_records("cyber_ratings")

    # Build lookup maps
    scan_map = {s.get("asset_id"): s for s in scan_results}
    pqc_map = {p.get("asset_id"): p for p in pqc_scores}
    hndl_map = {h.get("asset_id"): h for h in hndl_risks}
    rating_map = {r.get("asset_id"): r for r in cyber_ratings}

    # Count by type
    type_counts = {}
    risk_counts = {"Critical": 0, "Legacy": 0, "Standard": 0, "Elite-PQC": 0}
    expiring_30 = 0
    expired = 0
    high_risk = 0
    critical = 0
    pqc_ready_count = 0

    enriched_assets = []
    for asset in assets:
        aid = asset.get("id")
        scan = scan_map.get(aid, {})
        pqc = pqc_map.get(aid, {})
        hndl = hndl_map.get(aid, {})
        rating = rating_map.get(aid, {})

        atype = asset.get("asset_type", "Web App")
        type_counts[atype] = type_counts.get(atype, 0) + 1

        tier = rating.get("tier", "Standard")
        risk_counts[tier] = risk_counts.get(tier, 0) + 1

        days = scan.get("days_until_expiry", 999)
        is_exp = scan.get("is_expired", False)
        if is_exp:
            expired += 1
        elif days <= 30:
            expiring_30 += 1

        if tier in ("Critical", "Legacy"):
            high_risk += 1
        if tier == "Critical":
            critical += 1
        if pqc.get("pqc_ready"):
            pqc_ready_count += 1

        enriched_assets.append({
            **asset,
            "tls_version": scan.get("tls_version"),
            "cipher_suite": scan.get("cipher_suite"),
            "cert_key_size": scan.get("cert_key_size"),
            "days_until_expiry": scan.get("days_until_expiry"),
            "is_expired": scan.get("is_expired"),
            "issuer": scan.get("issuer"),
            "pqc_status": pqc.get("pqc_status"),
            "pqc_ready": pqc.get("pqc_ready"),
            "total_score": rating.get("total_score"),
            "tier": rating.get("tier"),
            "hndl_risk_level": hndl.get("hndl_risk_level"),
            "estimated_breach_year": hndl.get("estimated_breach_year"),
        })

    # Enterprise score
    enterprise = calculate_enterprise_rating(cyber_ratings) if cyber_ratings else {}

    # Nameserver-like records for dashboard table (demo)
    ns_records = [
        {"domain": "pnb.bank.in", "type": "NS", "value": "ns1.cloudflare.com", "ttl": 3600},
        {"domain": "pnb.bank.in", "type": "NS", "value": "ns2.cloudflare.com", "ttl": 3600},
        {"domain": "pnb.bank.in", "type": "MX", "value": "mail.pnb.bank.in", "ttl": 3600},
        {"domain": "pnb.bank.in", "type": "A", "value": "34.12.11.45", "ttl": 300},
    ]

    return success_response(data={
        "total_assets": len(assets),
        "web_apps": type_counts.get("Web App", 0),
        "apis": type_counts.get("API", 0),
        "servers": type_counts.get("Server", 0) + type_counts.get("Mail Server", 0),
        "gateways": type_counts.get("Gateway", 0),
        "expiring_certs_30d": expiring_30,
        "expired_certs": expired,
        "high_risk_assets": high_risk,
        "critical_assets": critical,
        "pqc_ready_count": pqc_ready_count,
        "pqc_ready_percentage": round(pqc_ready_count / max(len(assets), 1) * 100, 1),
        "enterprise_score": enterprise.get("total_score", 0),
        "enterprise_tier": enterprise.get("tier", "Standard"),
        "assets_by_type": type_counts,
        "assets_by_risk": risk_counts,
        "assets_by_tier": risk_counts,
        "assets": enriched_assets,
        "ns_records": ns_records,
        "recent_scans": get_records("audit_logs", limit=10),
    })


# ── Scan ─────────────────────────────────────────────────────────────────────

@app.post("/api/scan/start")
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Start a TLS scan for one or more domains."""
    # Validate and clean domains
    cleaned = []
    for d in request.domains:
        h = clean_hostname(d)
        if is_valid_hostname(h):
            cleaned.append(h)
        else:
            logger.warning(f"Invalid hostname skipped: {d}")

    if not cleaned:
        raise HTTPException(status_code=400, detail="No valid hostnames provided")

    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "target_domains": cleaned,
        "status": "pending",
        "total_assets": len(cleaned),
        "scanned_assets": 0,
        "started_at": utc_now(),
        "completed_at": None,
    }
    insert_record("scan_sessions", session)
    _scan_sessions[session_id] = session

    log_audit_event(
        action="scan_start",
        target=",".join(cleaned),
        metadata={"session_id": session_id, "domain_count": len(cleaned)}
    )

    background_tasks.add_task(_run_scan, session_id, cleaned, request.ports or [443])

    return success_response(
        data={"session_id": session_id, "domains": cleaned, "total": len(cleaned)},
        message=f"Scan started for {len(cleaned)} domain(s)"
    )


async def _run_scan(session_id: str, hostnames: List[str], ports: List[int]):
    """Background task: scan all hostnames and store results."""
    session = _scan_sessions.get(session_id, {})
    session["status"] = "running"
    upsert_record("scan_sessions", session)
    await _broadcast_progress(session_id, "running", 0, len(hostnames))

    for i, hostname in enumerate(hostnames):
        try:
            # TLS scan
            scan_data = await scan_domain(hostname)
            # Port scan (quick)
            port_data = await scan_ports(hostname, ports)
            # Classify
            classification = classify_asset(
                hostname,
                port_data.get("open_ports", []),
                scan_data.get("san", [])
            )

            asset_id = str(uuid.uuid4())

            # Resolve IP if not from scan
            ip = None
            try:
                import socket
                ip = socket.gethostbyname(hostname)
            except Exception:
                pass

            # Store asset
            asset_record = {
                "id": asset_id,
                "hostname": hostname,
                "url": f"https://{hostname}",
                "ip_address": ip,
                "asset_type": classification["asset_type"],
                "owner": classification["owner"],
                "ports": [p["port"] for p in port_data.get("open_ports", [])],
                "scan_session_id": session_id,
                "created_at": utc_now(),
                "updated_at": utc_now(),
            }
            insert_record("assets", asset_record)

            if scan_data.get("scan_success"):
                # Build all intelligence
                pqc_data = validate_pqc(scan_data)
                hndl_data = calculate_hndl_risk(scan_data, pqc_data)
                rating_data = calculate_cyber_rating(scan_data, pqc_data, hndl_data)
                cbom_entry = build_cbom_entry(scan_data)

                # Store scan result
                scan_record = {
                    "id": str(uuid.uuid4()), "asset_id": asset_id,
                    **{k: v for k, v in scan_data.items() if k not in ["hostname", "port"]},
                    "scanned_at": utc_now(),
                }
                insert_record("scan_results", scan_record)

                # Store CBOM
                cbom_record = {**cbom_entry, "id": str(uuid.uuid4()), "asset_id": asset_id}
                insert_record("cbom_entries", cbom_record)

                # Store scores
                pqc_rec = {**pqc_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": hostname}
                insert_record("pqc_scores", pqc_rec)
                hndl_rec = {**hndl_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": hostname}
                insert_record("hndl_risk", hndl_rec)
                rating_rec = {**rating_data, "id": str(uuid.uuid4()), "asset_id": asset_id, "hostname": hostname}
                insert_record("cyber_ratings", rating_rec)

            # Update progress
            session["scanned_assets"] = i + 1
            await _broadcast_progress(
                session_id, "running", i + 1, len(hostnames),
                current_host=hostname,
                result={"hostname": hostname, "success": scan_data.get("scan_success")}
            )

        except Exception as e:
            logger.error(f"Error scanning {hostname}: {e}")
            await _broadcast_progress(
                session_id, "running", i + 1, len(hostnames),
                current_host=hostname,
                result={"hostname": hostname, "success": False, "error": str(e)}
            )

    # Complete session
    session["status"] = "completed"
    session["completed_at"] = utc_now()
    upsert_record("scan_sessions", session)
    await _broadcast_progress(session_id, "completed", len(hostnames), len(hostnames))

    log_audit_event(
        action="scan_complete",
        target=",".join(hostnames[:3]),
        metadata={"session_id": session_id, "scanned": len(hostnames)}
    )


@app.get("/api/scan/status/{session_id}")
async def scan_status(session_id: str):
    """Get current scan session status."""
    session = _scan_sessions.get(session_id)
    if not session:
        db_session = get_record_by_id("scan_sessions", session_id)
        if not db_session:
            raise HTTPException(status_code=404, detail="Scan session not found")
        session = db_session

    return success_response(data=session)


@app.get("/api/scan/sessions")
async def list_scan_sessions():
    """List all scan sessions."""
    sessions = get_records("scan_sessions", limit=20)
    return success_response(data=sessions)


# ── Assets ────────────────────────────────────────────────────────────────────

@app.get("/api/assets")
async def get_assets():
    """Get all assets with enriched data."""
    assets = get_records("assets")
    scan_results = get_records("scan_results")
    pqc_scores = get_records("pqc_scores")
    hndl_risks = get_records("hndl_risk")
    cyber_ratings = get_records("cyber_ratings")

    scan_map = {s.get("asset_id"): s for s in scan_results}
    pqc_map = {p.get("asset_id"): p for p in pqc_scores}
    hndl_map = {h.get("asset_id"): h for h in hndl_risks}
    rating_map = {r.get("asset_id"): r for r in cyber_ratings}

    enriched = []
    for a in assets:
        aid = a.get("id")
        enriched.append({
            **a,
            "scan": scan_map.get(aid, {}),
            "pqc": pqc_map.get(aid, {}),
            "hndl": hndl_map.get(aid, {}),
            "rating": rating_map.get(aid, {}),
        })

    return success_response(data=enriched, message=f"{len(enriched)} assets found")


@app.get("/api/assets/{asset_id}")
async def get_asset(asset_id: str):
    """Get single asset with all intelligence data."""
    asset = get_record_by_id("assets", asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    scan_results = get_records("scan_results", {"asset_id": asset_id})
    pqc_scores = get_records("pqc_scores", {"asset_id": asset_id})
    hndl_risks = get_records("hndl_risk", {"asset_id": asset_id})
    cyber_ratings = get_records("cyber_ratings", {"asset_id": asset_id})
    cbom_entries = get_records("cbom_entries", {"asset_id": asset_id})
    migration_plans = get_records("migration_plans", {"asset_id": asset_id})

    return success_response(data={
        "asset": asset,
        "scan": scan_results[0] if scan_results else {},
        "pqc": pqc_scores[0] if pqc_scores else {},
        "hndl": hndl_risks[0] if hndl_risks else {},
        "rating": cyber_ratings[0] if cyber_ratings else {},
        "cbom": cbom_entries[0] if cbom_entries else {},
        "migration_plan": migration_plans[0] if migration_plans else None,
    })


# ── CBOM ──────────────────────────────────────────────────────────────────────

@app.get("/api/cbom")
async def get_cbom():
    """Get full Cryptographic Bill of Materials."""
    entries = get_records("cbom_entries")
    return success_response(data=entries, message=f"{len(entries)} CBOM entries")


@app.get("/api/cbom/export/{format}")
async def export_cbom(format: str):
    """Export CBOM in JSON, CSV, XML, or PDF format."""
    entries = get_records("cbom_entries")
    format = format.lower()

    if format == "json":
        content = export_json(entries)
        media_type = "application/json"
        filename = "quantumsight_cbom.json"
    elif format == "csv":
        content = export_csv(entries)
        media_type = "text/csv"
        filename = "quantumsight_cbom.csv"
    elif format == "xml":
        content = export_xml(entries)
        media_type = "application/xml"
        filename = "quantumsight_cbom.xml"
    elif format == "pdf":
        # Use executive report as PDF CBOM
        assets = get_records("assets")
        hndl = get_records("hndl_risk")
        ratings = get_records("cyber_ratings")
        summary = {"total_assets": len(assets), "enterprise_score": 0, "enterprise_tier": "Standard"}
        pdf_bytes = generate_executive_report(summary, assets, entries, ratings, hndl)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=quantumsight_cbom_report.pdf"}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    return StreamingResponse(
        io.BytesIO(content.encode() if isinstance(content, str) else content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ── PQC Posture ───────────────────────────────────────────────────────────────

@app.get("/api/pqc/posture")
async def pqc_posture():
    """Get enterprise-wide PQC posture summary."""
    pqc_scores = get_records("pqc_scores")
    assets = get_records("assets")
    scan_results = get_records("scan_results")

    asset_map = {a.get("id"): a for a in assets}
    scan_map = {s.get("asset_id"): s for s in scan_results}

    elite = sum(1 for p in pqc_scores if p.get("pqc_status") == "Elite-PQC")
    standard = sum(1 for p in pqc_scores if p.get("pqc_status") == "Standard")
    legacy = sum(1 for p in pqc_scores if p.get("pqc_status") == "Legacy")
    critical = sum(1 for p in pqc_scores if p.get("pqc_status") == "Critical")
    total = len(pqc_scores)

    recommendations = [
        "Migrate 3 critical assets (vpn.pnb.bank.in, legacy.pnb.bank.in) to TLS 1.3 + ML-KEM-768 immediately",
        "Replace TLS 1.1 reporting.pnb.bank.in — deprecated per RFC 8996",
        "Renew vpn.pnb.bank.in certificate (expiring in 12 days)",
        "Upgrade RSA-2048 key sizes to 3072-bit minimum per NIST SP 800-131A rev 2",
        "Implement HSTS headers on all Standard/Legacy tier assets",
        "Evaluate OQS-Provider for OpenSSL on TLS 1.3 endpoints for hybrid PQC deployment",
        "Conduct PQC readiness review for all payment-critical APIs",
        "Subscribe to DigiCert PQC certificate pilot for Elite-PQC certificate issuance",
    ]

    # Build detailed asset table
    detailed = []
    for p in pqc_scores:
        aid = p.get("asset_id")
        asset = asset_map.get(aid, {})
        scan = scan_map.get(aid, {})
        detailed.append({
            "hostname": asset.get("hostname", p.get("hostname", "")),
            "ip_address": asset.get("ip_address"),
            "asset_type": asset.get("asset_type"),
            "owner": asset.get("owner"),
            "pqc_status": p.get("pqc_status"),
            "pqc_ready": p.get("pqc_ready"),
            "tls_version": scan.get("tls_version"),
            "cipher_suite": scan.get("cipher_suite"),
            "vulnerability_reason": p.get("vulnerability_reason"),
            "recommended_replacement": p.get("recommended_replacement"),
            "gap_details": p.get("gap_details"),
        })

    return success_response(data={
        "total": total,
        "elite_pqc": elite,
        "standard": standard,
        "legacy": legacy,
        "critical": critical,
        "elite_percentage": round(elite / max(total, 1) * 100, 1),
        "quantum_vulnerable_count": total - elite,
        "assets": detailed,
        "recommendations": recommendations,
    })


# ── Cyber Rating ──────────────────────────────────────────────────────────────

@app.get("/api/cyber-rating")
async def enterprise_cyber_rating():
    """Get enterprise-level consolidated PQC cyber rating."""
    ratings = get_records("cyber_ratings")
    hndl_risks = get_records("hndl_risk")
    assets = get_records("assets")

    asset_map = {a.get("id"): a for a in assets}
    hndl_map = {h.get("asset_id"): h for h in hndl_risks}

    enterprise = calculate_enterprise_rating(ratings)

    # Enriched per-asset ratings
    enriched_ratings = []
    for r in ratings:
        aid = r.get("asset_id")
        asset = asset_map.get(aid, {})
        hndl = hndl_map.get(aid, {})
        enriched_ratings.append({
            **r,
            "hostname": asset.get("hostname", r.get("hostname", "")),
            "ip_address": asset.get("ip_address"),
            "asset_type": asset.get("asset_type"),
            "hndl_risk_level": hndl.get("hndl_risk_level"),
            "estimated_breach_year": hndl.get("estimated_breach_year"),
            "years_until_threat": hndl.get("years_until_threat"),
            "urgency": hndl.get("urgency"),
            "harvest_warning": hndl.get("harvest_warning"),
        })

    # Tier criteria table
    tier_criteria = [
        {"tier": "Critical", "range": "0–399", "tls": "SSL v2/v3", "action": "Isolate & replace immediately", "color": "red"},
        {"tier": "Legacy", "range": "400–699", "tls": "TLS 1.0/1.1", "action": "Replace within 6 months", "color": "amber"},
        {"tier": "Standard", "range": "700–849", "tls": "TLS 1.2", "action": "Migrate to PQC within 24 months", "color": "blue"},
        {"tier": "Elite-PQC", "range": "850–1000", "tls": "NIST PQC + TLS 1.3", "action": "Issue PQC-Ready Certificate", "color": "green"},
    ]

    return success_response(data={
        "enterprise": enterprise,
        "assets": enriched_ratings,
        "tier_criteria": tier_criteria,
    })


@app.get("/api/cyber-rating/{asset_id}")
async def asset_cyber_rating(asset_id: str):
    """Get per-asset cyber rating details."""
    ratings = get_records("cyber_ratings", {"asset_id": asset_id})
    if not ratings:
        raise HTTPException(status_code=404, detail="Rating not found for this asset")

    hndl = get_records("hndl_risk", {"asset_id": asset_id})
    return success_response(data={
        "rating": ratings[0],
        "hndl": hndl[0] if hndl else {}
    })


# ── AI Migration Copilot ──────────────────────────────────────────────────────

@app.post("/api/ai/migration-plan")
async def ai_migration_plan(request: MigrationPlanRequest):
    """Generate AI-powered PQC migration plan for an asset."""
    hostname = clean_hostname(request.hostname)

    # Get asset data
    assets = get_records("assets")
    asset = next((a for a in assets if a.get("hostname") == hostname), None)

    if not asset and request.asset_id:
        asset = get_record_by_id("assets", request.asset_id)

    if not asset:
        # Create minimal asset for non-scanned domain
        asset = {"id": "temp", "hostname": hostname, "asset_type": "Web App"}

    aid = asset.get("id")
    scan_results = get_records("scan_results", {"asset_id": aid}) if aid != "temp" else []
    pqc_scores = get_records("pqc_scores", {"asset_id": aid}) if aid != "temp" else []
    hndl_risks = get_records("hndl_risk", {"asset_id": aid}) if aid != "temp" else []

    scan_data = scan_results[0] if scan_results else {"hostname": hostname, "cipher_suite": "RSA-AES256-CBC", "tls_version": "TLS 1.2", "cert_key_size": 2048}
    pqc_data = pqc_scores[0] if pqc_scores else validate_pqc(scan_data)
    hndl_data = hndl_risks[0] if hndl_risks else calculate_hndl_risk(scan_data, pqc_data)

    scan_data["hostname"] = hostname

    log_audit_event("ai_plan_request", target=hostname)

    result = generate_migration_plan(scan_data, pqc_data, hndl_data)

    if result.get("success") and aid and aid != "temp":
        plan_record = {
            "id": str(uuid.uuid4()),
            "asset_id": aid,
            "plan": result["plan"],
            "ai_model": result["plan"].get("ai_model", "gemini-2.5-flash"),
            "generated_at": utc_now(),
        }
        insert_record("migration_plans", plan_record)

    return success_response(
        data=result,
        message="Migration plan generated successfully" if result["success"] else "Plan generated using template"
    )


# ── Certificates ──────────────────────────────────────────────────────────────

@app.get("/api/certificates/{asset_id}")
async def download_certificate(asset_id: str):
    """Download PQC-Ready PDF certificate for an Elite-PQC asset."""
    asset = get_record_by_id("assets", asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    pqc_list = get_records("pqc_scores", {"asset_id": asset_id})
    pqc_data = pqc_list[0] if pqc_list else {}

    if not pqc_data.get("pqc_ready"):
        # Still generate certificate but mark as "Assessment Certificate"
        pass

    scan_list = get_records("scan_results", {"asset_id": asset_id})
    scan_data = scan_list[0] if scan_list else {"hostname": asset.get("hostname")}

    rating_list = get_records("cyber_ratings", {"asset_id": asset_id})
    rating_data = rating_list[0] if rating_list else {"total_score": 0}

    scan_data["hostname"] = asset.get("hostname")
    asset["id"] = asset_id

    pdf_bytes = generate_pqc_certificate(asset, scan_data, pqc_data, rating_data)

    hostname = asset.get("hostname", "asset").replace(".", "_")
    log_audit_event("certificate_download", target=asset.get("hostname", ""))

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=PQC_Certificate_{hostname}.pdf"
        }
    )


# ── Discovery ─────────────────────────────────────────────────────────────────

@app.get("/api/discovery/domains")
async def discovery_domains():
    """Get discovered domain assets."""
    assets = get_records("assets")
    domains = [
        {
            "detection_date": a.get("created_at", utc_now())[:10],
            "domain_name": a.get("hostname"),
            "ip_address": a.get("ip_address"),
            "type": a.get("asset_type"),
            "owner": a.get("owner"),
            "status": "Confirmed"
        }
        for a in assets
    ]
    return success_response(data=domains)


@app.get("/api/discovery/ssl")
async def discovery_ssl():
    """Get discovered SSL certificates."""
    scan_results = get_records("scan_results")
    assets = get_records("assets")
    asset_map = {a.get("id"): a for a in assets}

    ssl_list = []
    for s in scan_results:
        asset = asset_map.get(s.get("asset_id"), {})
        from utils.helpers import extract_issuer_org
        ssl_list.append({
            "detection_date": s.get("scanned_at", utc_now())[:10],
            "sha256_fingerprint": s.get("sha256_fingerprint", "")[:32] + "...",
            "valid_from": s.get("not_valid_before", "")[:10],
            "valid_until": s.get("not_valid_after", "")[:10],
            "common_name": asset.get("hostname", ""),
            "issuer": extract_issuer_org(s.get("issuer", "")),
            "tls_version": s.get("tls_version"),
            "key_size": s.get("cert_key_size"),
            "is_expired": s.get("is_expired"),
            "days_until_expiry": s.get("days_until_expiry"),
            "status": "Confirmed"
        })
    return success_response(data=ssl_list)


@app.get("/api/discovery/ips")
async def discovery_ips():
    """Get discovered IP addresses."""
    assets = get_records("assets")
    ips = [
        {
            "detection_date": a.get("created_at", utc_now())[:10],
            "ip_address": a.get("ip_address", "N/A"),
            "ipv6_address": a.get("ipv6_address"),
            "ports": a.get("ports", [443]),
            "hostname": a.get("hostname"),
            "asset_type": a.get("asset_type"),
            "asn": "AS18018",  # Demo: PNB ASN
            "netname": "PNB-NET",
            "location": "Mumbai, India",
            "subnet": f"{a.get('ip_address', '34.0.0').rsplit('.', 1)[0]}.0/24" if a.get("ip_address") else "N/A",
            "status": "Confirmed"
        }
        for a in assets if a.get("ip_address")
    ]
    return success_response(data=ips)


@app.get("/api/discovery/software")
async def discovery_software():
    """Get discovered software/products from TLS scans."""
    scan_results = get_records("scan_results")
    assets = get_records("assets")
    asset_map = {a.get("id"): a for a in assets}

    software = []
    seen = set()
    tls_products = {
        "TLS 1.3": "OpenSSL 3.x / nginx 1.24",
        "TLS 1.2": "OpenSSL 1.1.x / Apache 2.4",
        "TLS 1.1": "OpenSSL 1.0.x (deprecated)",
        "TLS 1.0": "Legacy OpenSSL (EOL)",
        "SSLv3": "OpenSSL 0.9.x (critically EOL)",
    }
    for s in scan_results:
        asset = asset_map.get(s.get("asset_id"), {})
        tls = s.get("tls_version", "Unknown")
        product = tls_products.get(tls, "Unknown TLS Stack")
        key = f"{product}-{asset.get('hostname')}"
        if key not in seen:
            seen.add(key)
            software.append({
                "detection_date": s.get("scanned_at", utc_now())[:10],
                "product": product,
                "version": tls,
                "type": "TLS/SSL Library",
                "port": 443,
                "host": asset.get("hostname", ""),
                "company": asset.get("owner", ""),
                "status": "Confirmed"
            })
    return success_response(data=software)


# ── Network Graph ─────────────────────────────────────────────────────────────

@app.get("/api/discovery/graph")
async def discovery_graph():
    """Get D3.js network graph data (nodes and links)."""
    assets = get_records("assets")
    pqc_scores = get_records("pqc_scores")
    pqc_map = {p.get("asset_id"): p for p in pqc_scores}
    scan_results = get_records("scan_results")
    scan_map = {s.get("asset_id"): s for s in scan_results}

    nodes = []
    links = []

    # Central PNB node
    nodes.append({"id": "pnb_central", "label": "PNB Bank", "type": "bank", "group": "bank", "size": 30})

    from utils.helpers import extract_issuer_org
    ca_nodes_added = set()

    for asset in assets:
        aid = asset.get("id")
        pqc = pqc_map.get(aid, {})
        scan = scan_map.get(aid, {})
        status = pqc.get("pqc_status", "Standard")

        group_map = {"Elite-PQC": "safe", "Standard": "standard", "Legacy": "legacy", "Critical": "critical"}
        group = group_map.get(status, "standard")

        nodes.append({
            "id": aid,
            "label": asset.get("hostname", ""),
            "type": asset.get("asset_type", "Web App"),
            "group": group,
            "pqc_status": status,
            "score": 0,
            "size": 15,
            "ip": asset.get("ip_address"),
        })
        links.append({"source": "pnb_central", "target": aid, "type": "hosts"})

        # CA node
        issuer = scan.get("issuer", "")
        ca_name = extract_issuer_org(issuer)
        ca_id = f"ca_{ca_name.lower().replace(' ', '_')}"
        if ca_id not in ca_nodes_added:
            nodes.append({"id": ca_id, "label": ca_name, "type": "CA", "group": "ca", "size": 12})
            ca_nodes_added.add(ca_id)
        links.append({"source": aid, "target": ca_id, "type": "issued_by"})

    return success_response(data={"nodes": nodes, "links": links})


# ── Reports ───────────────────────────────────────────────────────────────────

@app.get("/api/reports/executive")
async def executive_report():
    """Get executive report data (JSON)."""
    assets = get_records("assets")
    cbom = get_records("cbom_entries")
    ratings = get_records("cyber_ratings")
    hndl = get_records("hndl_risk")
    pqc = get_records("pqc_scores")

    enterprise = calculate_enterprise_rating(ratings) if ratings else {}
    tier_dist = enterprise.get("tier_distribution", {})

    return success_response(data={
        "generated_at": utc_now(),
        "enterprise_score": enterprise.get("total_score", 0),
        "enterprise_tier": enterprise.get("tier", "Standard"),
        "total_assets": len(assets),
        "cbom_entries": len(cbom),
        "pqc_ready": sum(1 for p in pqc if p.get("pqc_ready")),
        "tier_distribution": tier_dist,
        "critical_count": tier_dist.get("Critical", 0),
        "assets": assets[:10],
    })


@app.post("/api/reports/export/{report_type}")
async def export_report(report_type: str, request: OnDemandReportRequest):
    """Generate and export on-demand report."""
    assets = get_records("assets")
    cbom = get_records("cbom_entries")
    ratings = get_records("cyber_ratings")
    hndl = get_records("hndl_risk")
    pqc = get_records("pqc_scores")
    enterprise = calculate_enterprise_rating(ratings) if ratings else {}

    fmt = request.file_format.lower()

    summary = {
        "total_assets": len(assets),
        "enterprise_score": enterprise.get("total_score", 0),
        "enterprise_tier": enterprise.get("tier", "Standard"),
        "assets_by_tier": enterprise.get("tier_distribution", {}),
        "pqc_ready_count": sum(1 for p in pqc if p.get("pqc_ready")),
    }

    if fmt == "pdf":
        pdf_bytes = generate_executive_report(summary, assets, cbom, ratings, hndl)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=QuantumSight_Report.pdf"}
        )
    elif fmt == "json":
        data = {"summary": summary, "assets": assets, "cbom": cbom}
        content = json.dumps(data, default=str, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=QuantumSight_Report.json"}
        )
    elif fmt == "csv":
        content = export_csv(cbom)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=QuantumSight_CBOM.csv"}
        )
    elif fmt == "xml":
        content = export_xml(cbom)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=QuantumSight_CBOM.xml"}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")


# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket("/ws/scan/{session_id}")
async def websocket_scan_progress(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time scan progress streaming."""
    await websocket.accept()
    _ws_connections[session_id] = websocket
    logger.info(f"WebSocket connected for session {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            # Echo back as keepalive
            await websocket.send_text(json.dumps({"type": "ping", "session_id": session_id}))
    except WebSocketDisconnect:
        _ws_connections.pop(session_id, None)
        logger.info(f"WebSocket disconnected for session {session_id}")


async def _broadcast_progress(
    session_id: str,
    status: str,
    scanned: int,
    total: int,
    current_host: str = "",
    result: dict = None
):
    """Send progress update to WebSocket client if connected."""
    ws = _ws_connections.get(session_id)
    if ws:
        try:
            percentage = round((scanned / max(total, 1)) * 100)
            await ws.send_text(json.dumps({
                "type": "progress",
                "session_id": session_id,
                "status": status,
                "scanned": scanned,
                "total": total,
                "percentage": percentage,
                "current_host": current_host,
                "result": result,
                "timestamp": utc_now()
            }))
        except Exception as e:
            logger.debug(f"WebSocket send failed for {session_id}: {e}")
            _ws_connections.pop(session_id, None)


# ── Audit Logs ────────────────────────────────────────────────────────────────

@app.get("/api/audit/logs")
async def audit_logs():
    logs = get_records("audit_logs", limit=100)
    return success_response(data=logs)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
