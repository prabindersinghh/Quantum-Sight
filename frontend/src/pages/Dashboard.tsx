import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
	PieChart,
	Pie,
	Cell,
	BarChart,
	Bar,
	XAxis,
	YAxis,
	Tooltip,
	ResponsiveContainer,
	Legend,
} from "recharts";
import {
	Globe,
	Database,
	Server,
	Shield,
	AlertTriangle,
	CheckCircle,
	TrendingUp,
	Clock,
	RefreshCw,
	Play,
} from "lucide-react";
import api from "../api/client";
import type { DashboardSummary, Asset } from "../types";
import PQCBadge from "../components/PQCBadge";
import ScanProgress from "../components/ScanProgress";

const TIER_COLORS = {
	"Elite-PQC": "#16A34A",
	Standard: "#2563EB",
	Legacy: "#D97706",
	Critical: "#DC2626",
};

function MetricCard({
	icon: Icon,
	label,
	value,
	sub,
	color = "default",
	onClick,
}: {
	icon: any;
	label: string;
	value: string | number;
	sub?: string;
	color?: "red" | "green" | "amber" | "blue" | "default";
	onClick?: () => void;
}) {
	const colorMap = {
		red: "bg-red-950/40 border-red-800/30",
		green: "bg-green-950/40 border-green-800/30",
		amber: "bg-amber-950/40 border-amber-800/30",
		blue: "bg-blue-950/40 border-blue-800/30",
		default: "bg-slate-800/60 border-slate-700/50",
	};
	const iconMap = {
		red: "text-red-400",
		green: "text-green-400",
		amber: "text-amber-400",
		blue: "text-blue-400",
		default: "text-slate-400",
	};
	const valMap = {
		red: "text-red-300",
		green: "text-green-300",
		amber: "text-amber-300",
		blue: "text-blue-300",
		default: "text-slate-100",
	};

	return (
		<div
			className={`rounded-xl p-4 border ${colorMap[color]} ${onClick ? "cursor-pointer hover:opacity-80" : ""} transition-opacity`}
			onClick={onClick}
		>
			<div className="flex items-start justify-between">
				<div>
					<div className="text-slate-400 text-xs font-medium mb-1">{label}</div>
					<div className={`text-2xl font-bold fade-up ${valMap[color]}`}>
						{value}
					</div>
					{sub && <div className="text-slate-500 text-xs mt-1">{sub}</div>}
				</div>
				<div className={`p-2 rounded-lg bg-slate-900/50 ${iconMap[color]}`}>
					<Icon size={18} />
				</div>
			</div>
		</div>
	);
}

function Skeleton() {
	return (
		<div className="space-y-4">
			<div className="grid grid-cols-4 gap-4">
				{[...Array(4)].map((_, i) => (
					<div key={i} className="h-24 shimmer rounded-xl" />
				))}
			</div>
			<div className="grid grid-cols-4 gap-4">
				{[...Array(4)].map((_, i) => (
					<div key={i} className="h-24 shimmer rounded-xl" />
				))}
			</div>
			<div className="grid grid-cols-2 gap-4">
				<div className="h-64 shimmer rounded-xl" />
				<div className="h-64 shimmer rounded-xl" />
			</div>
		</div>
	);
}

export default function Dashboard() {
	const [data, setData] = useState<DashboardSummary | null>(null);
	const [loading, setLoading] = useState(true);
	const [scanDomains, setScanDomains] = useState("");
	const [scanSession, setScanSession] = useState<string | null>(null);
	const [showScanForm, setShowScanForm] = useState(false);
	const navigate = useNavigate();

	const load = async () => {
		setLoading(true);
		try {
			const res = await api.getDashboard();
			setData(res.data.data);
		} catch (e) {
			console.error(e);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		load();
	}, []);

	const startScan = async () => {
		if (!scanDomains.trim()) return;
		const domains = scanDomains
			.split(/[\n,]+/)
			.map((d) => d.trim())
			.filter(Boolean);
		try {
			const res = await api.startScan(domains);
			setScanSession(res.data.data.session_id);
			setShowScanForm(false);
		} catch (e) {
			console.error(e);
		}
	};

	if (loading) return <Skeleton />;

	const byType = Object.entries(data?.assets_by_type || {}).map(
		([name, value]) => ({ name, value }),
	);
	const byTier = Object.entries(data?.assets_by_tier || {}).map(
		([name, value]) => ({ name, value }),
	);

	const TIER_PIE_COLORS = ["#DC2626", "#D97706", "#2563EB", "#16A34A"];

	return (
		<div className="space-y-5">
			{/* Scan Session Progress */}
			{scanSession && (
				<ScanProgress
					sessionId={scanSession}
					onComplete={() => {
						setScanSession(null);
						load();
					}}
				/>
			)}

			{/* Scan Form */}
			{showScanForm && (
				<div className="bg-slate-800/60 border border-amber-700/30 rounded-xl p-4">
					<div className="flex items-center justify-between mb-3">
						<h3 className="text-slate-200 font-semibold text-sm">
							Start New Scan
						</h3>
						<button
							onClick={() => setShowScanForm(false)}
							className="text-slate-500 hover:text-slate-300 text-xs"
						>
							Cancel
						</button>
					</div>
					<textarea
						value={scanDomains}
						onChange={(e) => setScanDomains(e.target.value)}
						placeholder="Enter domains to scan (one per line or comma-separated)&#10;e.g. portal.pnb.bank.in&#10;api.pnb.bank.in"
						className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-slate-200 text-sm placeholder-slate-600 focus:outline-none focus:border-amber-500 resize-none h-24"
					/>
					<div className="flex gap-2 mt-2">
						<button
							onClick={startScan}
							className="flex items-center gap-2 px-4 py-2 bg-pnb-red text-white rounded-lg text-sm font-medium hover:bg-red-800 transition-colors"
						>
							<Play size={14} /> Start Scan
						</button>
					</div>
				</div>
			)}

			{/* Row 1: Main metrics */}
			<div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
				<MetricCard
					icon={Globe}
					label="Total Assets"
					value={data?.total_assets || 0}
					sub="Public-facing"
				/>
				<MetricCard
					icon={Globe}
					label="Web Applications"
					value={data?.web_apps || 0}
					sub="Scanned"
				/>
				<MetricCard
					icon={Database}
					label="APIs"
					value={data?.apis || 0}
					sub="REST/GraphQL"
				/>
				<MetricCard
					icon={Server}
					label="Servers & Gateways"
					value={(data?.servers || 0) + (data?.gateways || 0)}
					sub="Infrastructure"
				/>
			</div>

			{/* Row 2: Risk metrics */}
			<div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
				<MetricCard
					icon={Clock}
					label="Expiring Certs (30d)"
					value={data?.expiring_certs_30d || 0}
					color="red"
					sub={`+${data?.expired_certs || 0} expired`}
				/>
				<MetricCard
					icon={AlertTriangle}
					label="High Risk Assets"
					value={data?.high_risk_assets || 0}
					color="red"
					sub="Critical + Legacy tier"
				/>
				<MetricCard
					icon={CheckCircle}
					label="PQC Ready"
					value={`${data?.pqc_ready_percentage || 0}%`}
					color="green"
					sub={`${data?.pqc_ready_count || 0} Elite-PQC assets`}
					onClick={() => navigate("/posture")}
				/>
				<MetricCard
					icon={TrendingUp}
					label="Enterprise Score"
					value={`${data?.enterprise_score || 0}/1000`}
					color="blue"
					sub={data?.enterprise_tier || "Standard"}
					onClick={() => navigate("/cyber-rating")}
				/>
			</div>

			{/* Row 3: Charts */}
			<div className="grid grid-cols-2 gap-4">
				{/* Asset Type Distribution */}
				<div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
					<h3 className="text-slate-300 text-sm font-semibold mb-4">
						Asset Type Distribution
					</h3>
					<ResponsiveContainer width="100%" height={200}>
						<PieChart>
							<Pie
								data={byType}
								cx="50%"
								cy="50%"
								innerRadius={55}
								outerRadius={85}
								paddingAngle={3}
								dataKey="value"
							>
								{byType.map((_, i) => (
									<Cell
										key={i}
										fill={
											[
												"#2563EB",
												"#7C3AED",
												"#D97706",
												"#16A34A",
												"#DC2626",
												"#0891B2",
											][i % 6]
										}
									/>
								))}
							</Pie>
							<Tooltip
								contentStyle={{
									background: "#fffff",
									border: "1px solid #334155",
									borderRadius: 8,
									color: "#F1F5F9",
									fontSize: 12,
								}}
							/>
							<Legend
								iconType="circle"
								iconSize={8}
								wrapperStyle={{ fontSize: 11, color: "#94A3B8" }}
							/>
						</PieChart>
					</ResponsiveContainer>
				</div>

				{/* Risk Distribution */}
				<div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
					<h3 className="text-slate-300 text-sm font-semibold mb-4">
						PQC Tier Distribution
					</h3>
					<ResponsiveContainer width="100%" height={200}>
						<BarChart
							data={byTier}
							margin={{ top: 0, right: 0, bottom: 0, left: -20 }}
						>
							<XAxis
								dataKey="name"
								tick={{ fill: "#64748B", fontSize: 11 }}
								axisLine={false}
								tickLine={false}
							/>
							<YAxis
								tick={{ fill: "#64748B", fontSize: 11 }}
								axisLine={false}
								tickLine={false}
							/>
							<Tooltip
								contentStyle={{
									background: "#1E293B",
									border: "1px solid #334155",
									borderRadius: 8,
									color: "#F1F5F9",
									fontSize: 12,
								}}
							/>
							<Bar dataKey="value" radius={[4, 4, 0, 0]}>
								{byTier.map((entry, i) => (
									<Cell
										key={i}
										fill={
											TIER_COLORS[entry.name as keyof typeof TIER_COLORS] ||
											"#64748B"
										}
									/>
								))}
							</Bar>
						</BarChart>
					</ResponsiveContainer>
				</div>
			</div>

			{/* Asset Table */}
			<div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
				<div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/50">
					<h3 className="text-slate-300 text-sm font-semibold">
						Asset Inventory
					</h3>
					<div className="flex items-center gap-2">
						<button
							onClick={() => setShowScanForm(true)}
							className="flex items-center gap-1.5 px-3 py-1.5 bg-pnb-red text-white rounded-lg text-xs font-medium hover:bg-red-800 transition-colors"
						>
							<Play size={11} /> New Scan
						</button>
						<button
							onClick={load}
							className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-600 transition-colors"
						>
							<RefreshCw size={11} /> Refresh
						</button>
					</div>
				</div>
				<div className="overflow-x-auto">
					<table className="w-full text-xs">
						<thead>
							<tr className="border-b border-slate-700/50">
								{[
									"Asset Name",
									"IPv4",
									"Type",
									"Owner",
									"Tier",
									"Cert Status",
									"Key Size",
									"Last Scan",
								].map((h) => (
									<th
										key={h}
										className="text-slate-500 font-medium text-left px-4 py-3"
									>
										{h}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{(data?.assets || []).map((asset) => (
								<tr
									key={asset.id}
									className="border-b border-slate-700/20 table-row-hover"
									onClick={() => navigate("/assets")}
								>
									<td className="px-4 py-3">
										<div className="text-slate-200 font-medium">
											{asset.hostname}
										</div>
										<div className="text-slate-500 text-xs mt-0.5">
											{asset.url}
										</div>
									</td>
									<td className="px-4 py-3 text-slate-400 font-mono">
										{asset.ip_address || "—"}
									</td>
									<td className="px-4 py-3 text-slate-400">
										{asset.asset_type}
									</td>
									<td className="px-4 py-3 text-slate-400 max-w-[120px] truncate">
										{asset.owner}
									</td>
									<td className="px-4 py-3">
										<PQCBadge
											status={asset.tier || asset.pqc_status || "Standard"}
											size="sm"
										/>
									</td>
									<td className="px-4 py-3">
										{asset.is_expired ? (
											<span className="text-red-400 font-semibold">
												EXPIRED
											</span>
										) : asset.days_until_expiry !== undefined ? (
											<span
												className={
													asset.days_until_expiry < 30
														? "text-amber-400"
														: "text-green-400"
												}
											>
												{asset.days_until_expiry}d
											</span>
										) : (
											"—"
										)}
									</td>
									<td className="px-4 py-3 text-slate-400">
										{asset.cert_key_size ? `${asset.cert_key_size}-bit` : "—"}
									</td>
									<td className="px-4 py-3 text-slate-500 text-xs">
										{asset.updated_at?.slice(0, 10) || "Today"}
									</td>
								</tr>
							))}
							{!data?.assets?.length && (
								<tr>
									<td colSpan={8} className="text-center py-8 text-slate-500">
										No assets found. Run a scan to populate the inventory.
									</td>
								</tr>
							)}
						</tbody>
					</table>
				</div>
			</div>

			{/* Nameserver Records */}
			{(data?.ns_records?.length || 0) > 0 && (
				<div className="bg-slate-800/60 border border-slate-700/50 rounded-xl overflow-hidden">
					<div className="px-5 py-3 border-b border-slate-700/50">
						<h3 className="text-slate-300 text-sm font-semibold">
							DNS / Nameserver Records
						</h3>
					</div>
					<table className="w-full text-xs">
						<thead>
							<tr className="border-b border-slate-700/50">
								{["Domain", "Type", "Value", "TTL"].map((h) => (
									<th
										key={h}
										className="text-slate-500 text-left px-4 py-3 font-medium"
									>
										{h}
									</th>
								))}
							</tr>
						</thead>
						<tbody>
							{data?.ns_records?.map((r, i) => (
								<tr key={i} className="border-b border-slate-700/20">
									<td className="px-4 py-2.5 text-slate-300 font-mono">
										{r.domain}
									</td>
									<td className="px-4 py-2.5">
										<span className="px-1.5 py-0.5 bg-blue-900/30 text-blue-400 rounded text-xs font-mono">
											{r.type}
										</span>
									</td>
									<td className="px-4 py-2.5 text-slate-400 font-mono">
										{r.value}
									</td>
									<td className="px-4 py-2.5 text-slate-500">{r.ttl}s</td>
								</tr>
							))}
						</tbody>
					</table>
				</div>
			)}

			{/* Recent Activity */}
			<div className="bg-slate-800/60 border border-slate-700/50 rounded-xl p-4">
				<h3 className="text-slate-300 text-sm font-semibold mb-3">
					Recent Activity
				</h3>
				<div className="space-y-2">
					{(data?.recent_scans?.length
						? data.recent_scans
						: [
								{
									id: "1",
									action: "scan_complete",
									target_domain: "pnb.bank.in domains",
									outcome: "success",
									timestamp: new Date().toISOString(),
								},
								{
									id: "2",
									action: "demo_seed",
									target_domain: "demo data loaded",
									outcome: "success",
									timestamp: new Date().toISOString(),
								},
							]
					)
						.slice(0, 8)
						.map((log) => (
							<div key={log.id} className="flex items-center gap-3 text-xs">
								<div
									className={`w-1.5 h-1.5 rounded-full shrink-0 ${log.outcome === "success" ? "bg-green-500" : "bg-red-500"}`}
								/>
								<span className="text-slate-300 font-medium capitalize">
									{log.action?.replace(/_/g, " ")}
								</span>
								{log.target_domain && (
									<span className="text-slate-500 truncate">
										{log.target_domain}
									</span>
								)}
								<span className="text-slate-600 ml-auto shrink-0">
									{log.timestamp?.slice(0, 19)?.replace("T", " ")}
								</span>
							</div>
						))}
				</div>
			</div>
		</div>
	);
}
