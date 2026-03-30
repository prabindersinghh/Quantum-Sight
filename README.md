# QuantumSight 🛡️⚛️

> **AI-Augmented Cryptographic Intelligence Platform**
> *Quantum-Ready Cybersecurity for Future-Safe Banking*

[![PNB Hackathon 2026](https://img.shields.io/badge/PNB%20Cybersecurity%20Hackathon-2026-8B0000?style=for-the-badge)](https://github.com/prabindersinghh/Quantum-Sight)
[![IIT Kanpur](https://img.shields.io/badge/In%20Collaboration%20With-IIT%20Kanpur-F59E0B?style=for-the-badge)](https://github.com/prabindersinghh/Quantum-Sight)
[![Team Incognito](https://img.shields.io/badge/Team-Incognito-1A1A2E?style=for-the-badge)](https://github.com/prabindersinghh/Quantum-Sight)
[![TIET Patiala](https://img.shields.io/badge/Institute-TIET%20Patiala-059669?style=for-the-badge)](https://thapar.edu)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

## 🎯 What Is QuantumSight?

QuantumSight is a **full-stack cryptographic intelligence platform** built for the **PNB Cybersecurity Hackathon 2026**, in collaboration with IIT Kanpur and the Ministry of Finance, Department of Financial Services, Government of India.

It automatically discovers every public-facing banking asset, analyses its cryptographic posture, calculates its **Harvest Now, Decrypt Later (HNDL) quantum risk window**, scores it on a 0–1000 scale, and generates AI-powered migration plans to NIST Post-Quantum Cryptography standards — per asset, per algorithm.

### The Problem We Solve

> Nation-state adversaries are **recording PNB's encrypted traffic RIGHT NOW** — storing it until quantum computers arrive to decrypt it.

Current banking cryptography (RSA, ECDSA, ECDH) is breakable by **Shor's Algorithm** on a Cryptanalytically Relevant Quantum Computer (CRQC). CRQCs are estimated to arrive by **2030–2035** (NIST/ENISA). The threat is not theoretical — it is active:

- **RSA-2048** → breakable by CRQC est. **2031** → HIGH HNDL risk
- **ECDHE-256 + TLS 1.2** → breakable by CRQC est. **2033** → HIGH risk
- **SSL v3 + RSA-1024** → **CRITICAL** — breakable classically today
- **ML-KEM-768 + TLS 1.3** → **SAFE** → PQC-Ready certificate issued

PNB has hundreds of public-facing assets with **no unified cryptographic inventory**. QuantumSight builds that inventory, quantifies the quantum risk, and tells you exactly what to fix.

---

## ✨ Key Features

| Feature | Description | Unique? |
|---------|-------------|---------|
| 🔍 **TLS Asset Scanner** | Async parallel scan of 50+ public assets simultaneously. Extracts all 22 CERT-IN Annexure-A CBOM fields from live TLS handshake | — |
| 📋 **Complete CBOM** | Full Cryptographic Bill of Materials per CERT-IN Annexure-A — Algorithms, Keys, Protocols, Certificates. Export JSON/CSV/XML/PDF | — |
| ⚠️ **HNDL Risk Engine** | Per-asset quantum decryption risk window. *"Intercepted traffic decryptable by 2031 — 5 years remaining."* CRITICAL/HIGH/MEDIUM/SAFE labels | **★ Unique** |
| ✅ **PQC Validator** | Validates each cipher against NIST FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA). Labels assets PQC-Ready or non-PQC | — |
| 🏆 **Cyber Rating 0–1000** | Composite score: TLS version + cipher strength + key size + cert validity + PQC readiness. Tiers: Critical / Legacy / Standard / Elite-PQC | — |
| 🤖 **AI Migration Copilot** | Gemini 2.5 Flash generates per-asset migration plan: specific NIST FIPS replacement, step-by-step instructions, library names, effort estimate | **★ Unique** |
| 🏅 **PQC Digital Certificate** | Downloadable PDF *"PQC Ready"* certificate for compliant assets — scan timestamp, NIST OIDs, digital assurance label | — |
| 📊 **Enterprise Reporting** | Executive, scheduled, on-demand reports. PDF/JSON/CSV/XML. Email delivery. RBAC: Admin/Checker/Viewer | — |
| 🕸️ **Interactive Network Graph** | D3.js force-directed graph of all discovered assets with PQC-status colour coding | — |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│         TIER 1 — PRESENTATION (React 18 + TypeScript)          │
│  Dashboard │ Asset Discovery │ CBOM │ PQC Posture │ Cyber Rating │ AI Copilot │ Reporting  │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API / WebSocket (HTTPS + TLS 1.3)
┌────────────────────────────▼────────────────────────────────────┐
│         TIER 2 — APPLICATION (Python 3.11 + FastAPI)           │
│  TLS Scanner │ CBOM Builder │ PQC Validator │ HNDL Engine      │
│  AI Copilot  │ Cyber Rating │ Cert Generator │ Report Engine   │
└────────────────────────────┬────────────────────────────────────┘
                             │ Supabase Client (Encrypted)
┌────────────────────────────▼────────────────────────────────────┐
│              TIER 3 — DATA (PostgreSQL 15 / Supabase)          │
│  assets │ scan_results │ cbom_entries │ pqc_scores │ hndl_risk  │
│  migration_plans │ certificates │ audit_logs │ scan_sessions   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
   Gemini 2.5            Public PNB           ReportLab
   Flash API             Endpoints            PDF Engine
   (AI Copilot)      (TLS scan target)    (Certs + Reports)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/prabindersinghh/Quantum-Sight.git
cd Quantum-Sight
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys (see Environment Variables section)
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

### 4. Run the Application

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

**Open:** [http://localhost:5173](http://localhost:5173)

The dashboard loads with **12 pre-seeded demo PNB assets** covering the full risk spectrum:

| Asset | Risk | TLS | Cipher | Breach Year |
|-------|------|-----|--------|-------------|
| `vpn.pnb.bank.in` | 🔴 CRITICAL | TLS 1.0 | DES | 2027 |
| `portal.pnb.bank.in` | 🟠 HIGH | TLS 1.2 | RSA-2048 | 2031 |
| `netbanking.pnb.bank.in` | 🟡 MEDIUM | TLS 1.2 | ECDHE-256 | 2033 |
| `pqc-api.pnb.bank.in` | 🟢 SAFE | TLS 1.3 | ML-KEM-768 | — |

---

## 🐳 Docker Setup (Recommended)

```bash
# Copy environment variables
cp .env.example .env

# Start everything
docker-compose up --build

# Access at http://localhost:5173
```

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
# ── Gemini AI (for AI Migration Copilot) ──────────────────────
# Get free key: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# ── Supabase (for persistent DB) ──────────────────────────────
# Get free project: https://supabase.com
# Leave blank to use in-memory demo store
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_DB_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# ── App ────────────────────────────────────────────────────────
SECRET_KEY=your_secret_key_here_min_32_chars
ENVIRONMENT=development
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# ── Scan Settings ──────────────────────────────────────────────
MAX_CONCURRENT_SCANS=50
SCAN_TIMEOUT_SECONDS=30
```

> **Note:** All keys are optional for the demo. Without `GEMINI_API_KEY`, the AI Copilot uses rich pre-built migration templates. Without Supabase credentials, the app runs with in-memory demo data.

---

## 📁 Project Structure

```
quantumsight/
├── backend/
│   ├── main.py                    # FastAPI app + all API routes
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   ├── scanner/
│   │   ├── tls_scanner.py         # Core TLS handshake + cert extraction
│   │   ├── domain_discovery.py    # DNS enumeration + subdomain discovery
│   │   ├── port_scanner.py        # Port 80/443/8443 scanning
│   │   └── asset_classifier.py    # Classify: WebApp/API/VPN/Server
│   ├── cbom/
│   │   ├── cbom_builder.py        # Maps scan data → all 22 Annexure-A fields
│   │   └── cbom_exporter.py       # JSON/CSV/XML/PDF export
│   ├── intelligence/
│   │   ├── pqc_validator.py       # NIST FIPS 203/204/205 validation
│   │   ├── hndl_engine.py         # HNDL risk window calculation
│   │   ├── cyber_rating.py        # 0-1000 composite scoring engine
│   │   └── ai_copilot.py          # Gemini API integration
│   ├── reports/
│   │   ├── pdf_certificate.py     # PQC-Ready PDF certificate generator
│   │   └── report_generator.py    # Executive/scheduled/on-demand reports
│   ├── database/
│   │   ├── supabase_client.py     # Supabase connection + in-memory fallback
│   │   └── models.py              # Pydantic models
│   └── utils/
│       └── helpers.py
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.tsx       # Home — summary metrics
│       │   ├── AssetInventory.tsx  # Asset table with filters
│       │   ├── AssetDiscovery.tsx  # Domains/SSL/IPs/Software tabs
│       │   ├── CBOM.tsx            # Cryptographic Bill of Materials
│       │   ├── PosturePQC.tsx      # PQC compliance dashboard
│       │   ├── CyberRating.tsx     # 0-1000 scoring + HNDL timeline
│       │   ├── AICopilot.tsx       # AI migration plan panel
│       │   └── Reporting.tsx       # Export + certificates
│       └── components/
│           ├── NetworkGraph.tsx    # D3.js force-directed graph
│           ├── HNDLCountdown.tsx   # Risk window display
│           ├── PQCBadge.tsx        # Quantum status badge
│           └── ScanProgress.tsx    # Real-time WebSocket scan progress
├── docker-compose.yml
└── README.md
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/scan/start` | Start scan for domain(s) |
| `GET` | `/api/scan/status/{session_id}` | Get scan progress |
| `GET` | `/api/assets` | Get all assets with filters |
| `GET` | `/api/cbom` | Get full CBOM |
| `GET` | `/api/cbom/export/{format}` | Export CBOM (json/csv/xml/pdf) |
| `GET` | `/api/pqc/posture` | Get PQC posture summary |
| `GET` | `/api/cyber-rating` | Get enterprise rating |
| `POST` | `/api/ai/migration-plan` | Generate AI migration plan |
| `GET` | `/api/certificates/{asset_id}` | Download PQC certificate (PDF) |
| `GET` | `/api/reports/executive` | Executive summary report |
| `GET` | `/api/dashboard/summary` | Dashboard metrics |
| `WS` | `/ws/scan/{session_id}` | Real-time scan progress |

Full interactive API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔐 CERT-IN Annexure-A CBOM Coverage

QuantumSight automatically populates all 22 minimum elements from CERT-IN Annexure-A:

| Asset Type | Elements Covered |
|-----------|-----------------|
| **Algorithms** | Name, Asset Type, Primitive, Mode, Crypto Functions, Classical Security Level, OID, Algorithm List |
| **Keys** | Name, Asset Type, ID, State, Size, Creation Date, Activation Date |
| **Protocols** | Name, Asset Type, Version, Cipher Suites, OID |
| **Certificates** | Subject Name, Issuer Name, Not Valid Before, Not Valid After, Signature Algorithm Ref, Subject Public Key Ref, Certificate Format, Certificate Extension |

All fields sourced directly from live TLS handshake — **zero manual input required**.

---

## 🧪 HNDL Risk Engine — How It Works

The HNDL (Harvest Now, Decrypt Later) Risk Engine is **unique to QuantumSight**.

```
Cipher Strength (classical bits)
         ↓
CRQC Timeline Estimate (NIST/ENISA 2030–2035)
         ↓
Years Until Decryption Threat = breach_year - current_year
         ↓
Risk Level Assignment:
  • SAFE      → PQC algorithm (no classical threat)
  • MEDIUM    → 8–12 years remaining
  • HIGH      → 5–8 years remaining
  • CRITICAL  → <5 years or already classically broken
```

| Algorithm | Classical Security | Breach Year | Risk |
|-----------|-------------------|-------------|------|
| SSL v2/v3 + RSA-512 | <80 bit | NOW | 🔴 CRITICAL |
| RSA-2048 + TLS 1.0/1.1 | 112 bit | ~2031 | 🟠 HIGH |
| ECDHE-256 + TLS 1.2 | 128 bit | ~2033 | 🟠 HIGH |
| ECDHE-384 + TLS 1.3 | 192 bit | ~2036 | 🟡 MEDIUM |
| ML-KEM-768 + TLS 1.3 | Quantum-safe | — | 🟢 SAFE |

---

## 🏆 Cyber Rating System

Each asset receives a **0–1000 composite score**:

| Component | Weight | Criteria |
|-----------|--------|----------|
| TLS Version | 200 pts | TLS 1.3=200 / TLS 1.2=140 / TLS 1.1=60 / TLS 1.0=20 / SSL=0 |
| Cipher Strength | 200 pts | ChaCha20/AES-256-GCM=200 / AES-128-GCM=160 / AES-CBC=80 / 3DES=0 |
| Key Size | 150 pts | ≥4096=150 / ≥3072=130 / ≥2048=100 / ≥1024=30 / <1024=0 |
| Certificate Validity | 150 pts | >90 days=150 / 30-90 days=80 / <30 days=20 / Expired=0 |
| PQC Readiness | 300 pts | NIST PQC=300 / Standard=100 / Legacy=30 / Critical=0 |

**Tiers:**
- 🔴 **Critical** (0–399): Immediate action — isolate and replace
- 🟠 **Legacy** (400–699): Remediation required within 6 months
- 🔵 **Standard** (700–849): Good posture — plan PQC migration
- 🟢 **Elite-PQC** (850–1000): Quantum-ready — PQC certificate issued

---

## 🔬 NIST PQC Algorithms Supported

| Algorithm | FIPS Standard | Type | Security Level |
|-----------|--------------|------|---------------|
| ML-KEM-768 (Kyber) | FIPS 203 | Key Encapsulation | Level 3 |
| ML-DSA-65 (Dilithium) | FIPS 204 | Digital Signature | Level 3 |
| SLH-DSA-SHA2-128S (SPHINCS+) | FIPS 205 | Hash-based Signature | Level 1 |
| FALCON-512/1024 | FIPS 206 | Lattice Signature | Level 1/5 |

---

## 🏅 Hackathon Context

**PNB Cybersecurity Hackathon 2026**
Theme: *Hackathon Cyber Security: Quantum-Proof Systems*
Problem Statement: Develop a software scanner to validate deployment of Quantum-proof ciphers and create a Cryptographic Bill of Material inventory for public-facing applications
Organized by: **Punjab National Bank + IIT Kanpur**
Initiative of: Government of India, Ministry of Finance, Department of Financial Services

### The Three Differentiators

1. **HNDL Risk Countdown** — Shows exactly when intercepted traffic becomes decryptable: *"This API's traffic is decryptable by 2031 — 5 years remaining."* Per-asset, with countdown and urgency bar.

2. **Live AI Migration Plan** — Gemini 2.5 Flash generates real NIST-specific migration roadmaps with actual library names, CLI commands, and CERT-IN compliance notes.

3. **PQC Certificate Download** — Issue a beautiful PDF certificate for a quantum-safe asset during the demo. Hand it to the judge.

---

## 👥 Team

**Team Incognito — Thapar Institute of Engineering & Technology, Patiala**

| Name | Role | Responsibility |
|------|------|---------------|
| **Prabinder Singh** | Team Lead | Architecture, Backend, AI Integration |
| **Deepesh Kakkar** | Developer | Frontend, UI/UX, React Dashboard |
| **Suyash Sahota** | Developer | Scanner Engine, CBOM Builder |
| **Ambreen Suri** | Tester | QA, Security Testing, Documentation |

---

## 🙏 Acknowledgements

- [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography) — FIPS 203/204/205 standards
- [CERT-In](https://www.cert-in.org.in/) — CBOM Annexure-A framework
- [Open Quantum Safe (liboqs)](https://openquantumsafe.org/) — PQC algorithm implementations
- [Punjab National Bank](https://www.pnbindia.in/) & [IIT Kanpur](https://www.iitk.ac.in/) — for organizing this hackathon

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**QuantumSight** — Built with ❤️ by Team Incognito
*Thapar Institute of Engineering & Technology, Patiala*
*PNB Cybersecurity Hackathon 2026*

</div>
