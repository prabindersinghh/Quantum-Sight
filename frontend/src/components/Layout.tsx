import { useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Database, Globe, Shield, ShieldCheck,
  BarChart3, Bot, FileText, ChevronLeft, ChevronRight,
  Bell, User, Wifi, WifiOff
} from 'lucide-react'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/assets', label: 'Asset Inventory', icon: Database },
  { path: '/discovery', label: 'Asset Discovery', icon: Globe },
  { path: '/cbom', label: 'CBOM', icon: Shield },
  { path: '/posture', label: 'PQC Posture', icon: ShieldCheck },
  { path: '/cyber-rating', label: 'Cyber Rating', icon: BarChart3 },
  { path: '/ai-copilot', label: 'AI Copilot', icon: Bot, badge: 'NEW' },
  { path: '/reporting', label: 'Reporting', icon: FileText },
]

const PAGE_NAMES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/assets': 'Asset Inventory',
  '/discovery': 'Asset Discovery',
  '/cbom': 'Cryptographic Bill of Materials',
  '/posture': 'PQC Posture Assessment',
  '/cyber-rating': 'PQC Cyber Rating',
  '/ai-copilot': 'AI Migration Copilot',
  '/reporting': 'Reports & Certificates',
}

export default function Layout({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const location = useLocation()
  const pageName = PAGE_NAMES[location.pathname] || 'QuantumSight'

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      {/* Sidebar */}
      <aside
        className="flex flex-col border-r border-slate-700/50 bg-slate-900 transition-all duration-300 shrink-0"
        style={{ width: collapsed ? 64 : 240 }}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-4 border-b border-slate-700/50 bg-pnb-red" style={{ minHeight: 64 }}>
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-white/20 shrink-0">
            <span className="text-white font-black text-sm tracking-tight">pnb</span>
          </div>
          {!collapsed && (
            <div className="overflow-hidden">
              <div className="text-white font-bold text-sm leading-none">QuantumSight</div>
              <div className="text-red-200 text-xs mt-0.5 whitespace-nowrap">PQC Intelligence</div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-3 overflow-y-auto overflow-x-hidden">
          {NAV_ITEMS.map(({ path, label, icon: Icon, badge }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm font-medium transition-all duration-150 group relative
                ${isActive
                  ? 'bg-red-950/60 text-red-400 border border-red-900/40'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
              title={collapsed ? label : undefined}
            >
              <Icon size={17} className="shrink-0" />
              {!collapsed && (
                <>
                  <span className="truncate">{label}</span>
                  {badge && (
                    <span className="ml-auto text-xs font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                      {badge}
                    </span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        {!collapsed && (
          <div className="px-4 py-3 border-t border-slate-700/50">
            <div className="text-slate-500 text-xs">QuantumSight v1.0</div>
            <div className="text-slate-600 text-xs mt-0.5">PNB Hackathon 2026</div>
          </div>
        )}

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center h-10 border-t border-slate-700/50 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-colors"
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </aside>

      {/* Main content */}
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-3 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur shrink-0" style={{ height: 64 }}>
          <div>
            <h1 className="text-slate-100 font-semibold text-base">{pageName}</h1>
            <div className="text-slate-500 text-xs mt-0.5">
              CERT-IN Annexure-A | NIST FIPS 203/204/205
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-green-900/30 border border-green-700/30 text-green-400 text-xs font-medium">
              <Wifi size={11} />
              Live
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-amber-900/20 border border-amber-700/30 text-amber-400 text-xs font-medium">
              <Shield size={11} />
              CERT-IN Auditor
            </div>
            <button className="relative p-2 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition-colors">
              <Bell size={16} />
              <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500"></span>
            </button>
            <div className="flex items-center gap-2 pl-2 border-l border-slate-700">
              <div className="w-7 h-7 rounded-full bg-pnb-red flex items-center justify-center">
                <User size={13} className="text-white" />
              </div>
              <div className="text-xs">
                <div className="text-slate-200 font-medium">Admin</div>
                <div className="text-slate-500">pnb.bank.in</div>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-950">
          {children}
        </main>
      </div>
    </div>
  )
}
