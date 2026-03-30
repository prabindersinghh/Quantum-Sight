import axios from 'axios'
import type { APIResponse, Asset, DashboardSummary, CBOMEntry, PQCScore, HNDLRisk, CyberRating, MigrationPlan, ScanSession } from '../types'

const API = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

API.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error('API Error:', err.response?.data || err.message)
    return Promise.reject(err)
  }
)

export const api = {
  getDashboard: () =>
    API.get<APIResponse<DashboardSummary>>('/dashboard/summary'),

  startScan: (domains: string[], ports?: number[], includeSubdomains?: boolean) =>
    API.post<APIResponse<{ session_id: string; domains: string[] }>>('/scan/start', {
      domains,
      ports: ports || [443],
      include_subdomains: includeSubdomains || false,
    }),
  getScanStatus: (sessionId: string) =>
    API.get<APIResponse<ScanSession>>(`/scan/status/${sessionId}`),
  getScanSessions: () =>
    API.get<APIResponse<ScanSession[]>>('/scan/sessions'),

  getAssets: () =>
    API.get<APIResponse<Asset[]>>('/assets'),
  getAsset: (id: string) =>
    API.get<APIResponse<{
      asset: Asset; scan: any; pqc: PQCScore; hndl: HNDLRisk; rating: CyberRating; cbom: CBOMEntry; migration_plan: any
    }>>(`/assets/${id}`),

  getCBOM: () =>
    API.get<APIResponse<CBOMEntry[]>>('/cbom'),
  exportCBOM: (format: string) =>
    API.get(`/cbom/export/${format}`, { responseType: 'blob' }),

  getPQCPosture: () =>
    API.get<APIResponse<any>>('/pqc/posture'),

  getCyberRating: () =>
    API.get<APIResponse<any>>('/cyber-rating'),
  getAssetRating: (id: string) =>
    API.get<APIResponse<any>>(`/cyber-rating/${id}`),

  generateMigrationPlan: (hostname: string, assetId?: string) =>
    API.post<APIResponse<{ success: boolean; plan: MigrationPlan }>>('/ai/migration-plan', {
      hostname,
      asset_id: assetId,
    }),

  getDiscoveryDomains: () =>
    API.get<APIResponse<any[]>>('/discovery/domains'),
  getDiscoverySSL: () =>
    API.get<APIResponse<any[]>>('/discovery/ssl'),
  getDiscoveryIPs: () =>
    API.get<APIResponse<any[]>>('/discovery/ips'),
  getDiscoverySoftware: () =>
    API.get<APIResponse<any[]>>('/discovery/software'),
  getNetworkGraph: () =>
    API.get<APIResponse<{ nodes: any[]; links: any[] }>>('/discovery/graph'),

  getExecutiveReport: () =>
    API.get<APIResponse<any>>('/reports/executive'),
  exportReport: (reportType: string, format: string) =>
    API.post(`/reports/export/${reportType}`, { report_types: [reportType], file_format: format }, { responseType: 'blob' }),

  downloadCertificate: (assetId: string) =>
    API.get(`/certificates/${assetId}`, { responseType: 'blob' }),

  health: () => API.get('/health'),
}

export default api
