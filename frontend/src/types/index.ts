export interface Asset {
  id: string
  hostname: string
  url?: string
  ip_address?: string
  ipv6_address?: string
  asset_type: string
  owner: string
  ports?: number[]
  scan_session_id?: string
  created_at?: string
  updated_at?: string
  // Enriched
  tls_version?: string
  cipher_suite?: string
  cert_key_size?: number
  days_until_expiry?: number
  is_expired?: boolean
  issuer?: string
  pqc_status?: string
  pqc_ready?: boolean
  total_score?: number
  tier?: string
  hndl_risk_level?: string
  estimated_breach_year?: number
  scan?: ScanResult
  pqc?: PQCScore
  hndl?: HNDLRisk
  rating?: CyberRating
}

export interface ScanResult {
  id?: string
  asset_id?: string
  tls_version?: string
  cipher_suite?: string
  key_bits?: number
  cert_key_size?: number
  cert_key_type?: string
  signature_algorithm?: string
  signature_algorithm_oid?: string
  subject?: string
  issuer?: string
  not_valid_before?: string
  not_valid_after?: string
  serial_number?: string
  sha256_fingerprint?: string
  san?: string[]
  is_expired?: boolean
  days_until_expiry?: number
  scan_success?: boolean
  scanned_at?: string
}

export interface PQCScore {
  id?: string
  asset_id?: string
  pqc_ready: boolean
  pqc_status: 'Elite-PQC' | 'Standard' | 'Legacy' | 'Critical'
  fips_standard?: string
  quantum_vulnerable?: boolean
  vulnerability_reason?: string
  recommended_replacement?: {
    algorithm: string
    fips: string
    oid: string
    purpose: string
    security_level: number
    library: string
    migration_effort: string
  }
  gap_details?: string
}

export interface HNDLRisk {
  id?: string
  asset_id?: string
  hostname?: string
  hndl_risk_level: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  hndl_risk_score: number
  years_until_threat?: number
  estimated_breach_year?: number
  classical_security_bits?: number
  risk_color?: string
  risk_description?: string
  urgency?: string
  harvest_warning?: string
}

export interface CyberRating {
  id?: string
  asset_id?: string
  hostname?: string
  total_score: number
  tier: 'Elite-PQC' | 'Standard' | 'Legacy' | 'Critical'
  tier_color?: string
  tier_description?: string
  breakdown?: Record<string, { score: number; max: number; detail: string }>
  percentage?: number
  hndl_risk_level?: string
  estimated_breach_year?: number
  years_until_threat?: number
  urgency?: string
  harvest_warning?: string
}

export interface CBOMEntry {
  id?: string
  asset_id?: string
  hostname?: string
  algo_name?: string
  algo_primitive?: string
  algo_mode?: string
  algo_classical_security_level?: number
  algo_oid?: string
  key_name?: string
  key_size?: number
  key_state?: string
  key_creation_date?: string
  protocol_name?: string
  protocol_version?: string
  protocol_cipher_suites?: string
  cert_name?: string
  cert_subject_name?: string
  cert_issuer_name?: string
  cert_not_valid_before?: string
  cert_not_valid_after?: string
  cert_signature_algorithm_ref?: string
  cert_format?: string
  cert_sha256_fingerprint?: string
  days_until_expiry?: number
  is_expired?: boolean
}

export interface DashboardSummary {
  total_assets: number
  web_apps: number
  apis: number
  servers: number
  gateways: number
  expiring_certs_30d: number
  expired_certs: number
  high_risk_assets: number
  critical_assets: number
  pqc_ready_count: number
  pqc_ready_percentage: number
  enterprise_score: number
  enterprise_tier: string
  assets_by_type: Record<string, number>
  assets_by_risk: Record<string, number>
  assets_by_tier: Record<string, number>
  assets: Asset[]
  ns_records: NameserverRecord[]
  recent_scans: AuditLog[]
}

export interface NameserverRecord {
  domain: string
  type: string
  value: string
  ttl: number
}

export interface AuditLog {
  id: string
  action: string
  target_domain?: string
  outcome?: string
  timestamp: string
}

export interface MigrationPlan {
  summary: string
  priority: string
  effort_estimate: string
  estimated_timeline: string
  business_impact?: string
  replacement_algorithm: {
    name: string
    fips_standard: string
    oid: string
    security_level: number | string
    quantum_security_bits?: string
  }
  migration_steps: Array<{
    step: number
    title: string
    description: string
    commands: string[]
    estimated_time: string
    dependencies?: string
  }>
  recommended_libraries: Array<{
    name: string
    language: string
    install: string
    purpose: string
    maturity?: string
  }>
  risks: string[]
  hybrid_approach?: string
  testing_approach: string
  rollback_plan: string
  compliance_notes: string
  cert_in_alignment?: string
  cost_estimate?: string
  generated_at?: string
  hostname?: string
  ai_model?: string
  ai_generated?: boolean
}

export interface ScanSession {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  target_domains: string[]
  total_assets: number
  scanned_assets: number
  started_at: string
  completed_at?: string
}

export interface APIResponse<T> {
  success: boolean
  data: T
  message: string
  timestamp: string
}

export interface NetworkNode {
  id: string
  label: string
  type: string
  group: string
  pqc_status?: string
  size?: number
  ip?: string
}

export interface NetworkLink {
  source: string
  target: string
  type: string
}
