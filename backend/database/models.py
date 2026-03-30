"""
Pydantic models for all QuantumSight entities.
Used for request/response validation in FastAPI endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    WEB_APP = "Web App"
    API = "API"
    VPN = "VPN"
    SERVER = "Server"
    GATEWAY = "Gateway"
    MAIL_SERVER = "Mail Server"
    CDN = "CDN/Static"
    AUTH = "Auth/SSO"
    LOAD_BALANCER = "Load Balancer"


class PQCStatus(str, Enum):
    ELITE_PQC = "Elite-PQC"
    STANDARD = "Standard"
    LEGACY = "Legacy"
    CRITICAL = "Critical"


class HNDLRiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ScanTier(str, Enum):
    ELITE_PQC = "Elite-PQC"
    STANDARD = "Standard"
    LEGACY = "Legacy"
    CRITICAL = "Critical"


# ── Request Models ──────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    domains: List[str] = Field(..., description="List of domains to scan")
    ports: Optional[List[int]] = Field(default=[443], description="Ports to scan")
    include_subdomains: bool = Field(default=False)
    max_concurrent: int = Field(default=10, le=50)


class MigrationPlanRequest(BaseModel):
    hostname: str
    asset_id: Optional[str] = None


class ScheduledReportRequest(BaseModel):
    report_type: str
    frequency: str  # weekly/monthly
    assets: Optional[List[str]] = None
    include_sections: Optional[List[str]] = None
    delivery_email: Optional[str] = None
    schedule_time: Optional[str] = None
    timezone: str = "Asia/Kolkata"


class OnDemandReportRequest(BaseModel):
    report_types: List[str]
    file_format: str = "pdf"  # pdf/json/csv/xml
    include_charts: bool = True
    password_protect: bool = False
    asset_ids: Optional[List[str]] = None


# ── Response Models ──────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ScanSessionResponse(BaseModel):
    session_id: str
    status: str
    total_assets: int = 0
    scanned_assets: int = 0
    started_at: str
    completed_at: Optional[str] = None
    message: str = ""


class AssetModel(BaseModel):
    id: Optional[str] = None
    hostname: str
    url: Optional[str] = None
    ip_address: Optional[str] = None
    ipv6_address: Optional[str] = None
    asset_type: str = "Web App"
    owner: str = "IT Operations Team"
    ports: Optional[List[int]] = None
    scan_session_id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ScanResultModel(BaseModel):
    id: Optional[str] = None
    asset_id: Optional[str] = None
    tls_version: Optional[str] = None
    cipher_suite: Optional[str] = None
    key_bits: Optional[int] = None
    cert_key_size: Optional[int] = None
    cert_key_type: Optional[str] = None
    signature_algorithm: Optional[str] = None
    signature_algorithm_oid: Optional[str] = None
    subject: Optional[str] = None
    issuer: Optional[str] = None
    not_valid_before: Optional[str] = None
    not_valid_after: Optional[str] = None
    serial_number: Optional[str] = None
    sha256_fingerprint: Optional[str] = None
    san: Optional[List[str]] = None
    is_expired: bool = False
    days_until_expiry: int = 0
    scan_success: bool = True
    error_message: Optional[str] = None
    scanned_at: Optional[str] = None


class CBOMEntryModel(BaseModel):
    id: Optional[str] = None
    asset_id: Optional[str] = None
    hostname: Optional[str] = None
    # Algorithm
    algo_name: Optional[str] = None
    algo_asset_type: str = "algorithm"
    algo_primitive: Optional[str] = None
    algo_mode: Optional[str] = None
    algo_crypto_functions: Optional[List[str]] = None
    algo_classical_security_level: Optional[int] = None
    algo_oid: Optional[str] = None
    # Key
    key_name: Optional[str] = None
    key_asset_type: str = "key"
    key_id: Optional[str] = None
    key_state: Optional[str] = None
    key_size: Optional[int] = None
    key_creation_date: Optional[str] = None
    key_activation_date: Optional[str] = None
    # Protocol
    protocol_name: Optional[str] = None
    protocol_asset_type: str = "protocol"
    protocol_version: Optional[str] = None
    protocol_cipher_suites: Optional[str] = None
    protocol_oid: Optional[str] = None
    # Certificate
    cert_name: Optional[str] = None
    cert_asset_type: str = "certificate"
    cert_subject_name: Optional[str] = None
    cert_issuer_name: Optional[str] = None
    cert_not_valid_before: Optional[str] = None
    cert_not_valid_after: Optional[str] = None
    cert_signature_algorithm_ref: Optional[str] = None
    cert_subject_public_key_ref: Optional[str] = None
    cert_format: str = "X.509"
    cert_extension: str = ".crt"
    cert_sha256_fingerprint: Optional[str] = None


class PQCScoreModel(BaseModel):
    id: Optional[str] = None
    asset_id: Optional[str] = None
    hostname: Optional[str] = None
    pqc_ready: bool = False
    pqc_status: str = "Standard"
    fips_standard: Optional[str] = None
    quantum_vulnerable: bool = True
    vulnerability_reason: Optional[str] = None
    recommended_replacement: Optional[Dict[str, Any]] = None
    gap_details: Optional[str] = None


class HNDLRiskModel(BaseModel):
    id: Optional[str] = None
    asset_id: Optional[str] = None
    hostname: Optional[str] = None
    hndl_risk_level: str = "MEDIUM"
    hndl_risk_score: int = 50
    years_until_threat: Optional[int] = None
    estimated_breach_year: Optional[int] = None
    classical_security_bits: Optional[int] = None
    risk_color: str = "amber"
    risk_description: Optional[str] = None
    urgency: Optional[str] = None


class CyberRatingModel(BaseModel):
    id: Optional[str] = None
    asset_id: Optional[str] = None
    hostname: Optional[str] = None
    total_score: int = 0
    tier: str = "Standard"
    tier_color: str = "blue"
    tier_description: Optional[str] = None
    breakdown: Optional[Dict[str, Any]] = None
    percentage: float = 0.0
    hndl_risk_level: Optional[str] = None
    estimated_breach_year: Optional[int] = None
    years_until_threat: Optional[int] = None


class DashboardSummary(BaseModel):
    total_assets: int = 0
    web_apps: int = 0
    apis: int = 0
    servers: int = 0
    gateways: int = 0
    expiring_certs_30d: int = 0
    expired_certs: int = 0
    high_risk_assets: int = 0
    critical_assets: int = 0
    pqc_ready_count: int = 0
    pqc_ready_percentage: float = 0.0
    enterprise_score: int = 0
    enterprise_tier: str = "Standard"
    assets_by_type: Dict[str, int] = {}
    assets_by_risk: Dict[str, int] = {}
    assets_by_tier: Dict[str, int] = {}
    recent_scans: List[Dict[str, Any]] = []
