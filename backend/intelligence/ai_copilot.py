"""
AI Migration Copilot — Generates per-asset PQC migration plans via Gemini API.
Uses gemini-2.5-flash to produce detailed, actionable migration roadmaps
with NIST FIPS replacement algorithms, steps, libraries, and timelines.
"""
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

_gemini_available = False
try:
    import google.generativeai as genai
    _gemini_available = True
except ImportError:
    logger.warning("google-generativeai not installed — AI Copilot will use fallback mode")


def generate_migration_plan(scan_data: dict, pqc_data: dict, hndl_data: dict) -> dict:
    """
    Generate an AI-powered PQC migration plan for a quantum-vulnerable asset.
    Uses Gemini 2.5 Flash. Falls back to a structured template if API unavailable.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")

    if not _gemini_available or not api_key or api_key == "your_gemini_api_key":
        return _fallback_plan(scan_data, pqc_data, hndl_data)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        prompt = _build_prompt(scan_data, pqc_data, hndl_data)
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        if "```" in text:
            parts = text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    text = part
                    break

        plan = json.loads(text)
        plan["generated_at"] = datetime.now().isoformat()
        plan["hostname"] = scan_data.get("hostname")
        plan["ai_model"] = "gemini-2.5-flash"
        plan["ai_generated"] = True

        return {"success": True, "plan": plan}

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from Gemini response: {e}")
        return _fallback_plan(scan_data, pqc_data, hndl_data)
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return _fallback_plan(scan_data, pqc_data, hndl_data)


def _build_prompt(scan_data: dict, pqc_data: dict, hndl_data: dict) -> str:
    return f"""You are a Post-Quantum Cryptography migration expert advising Punjab National Bank (PNB), India's second-largest public sector bank.

Asset Under Analysis:
- Domain: {scan_data.get('hostname')}
- TLS Version: {scan_data.get('tls_version')}
- Cipher Suite: {scan_data.get('cipher_suite')}
- Key Type/Size: {scan_data.get('cert_key_type', 'RSA')}-{scan_data.get('cert_key_size')} bits
- Certificate Expiry: {scan_data.get('days_until_expiry')} days remaining
- Certificate Issuer: {scan_data.get('issuer', 'Unknown')}

Quantum Risk Assessment:
- HNDL Risk Level: {hndl_data.get('hndl_risk_level')}
- Estimated CRQC Threat Year: {hndl_data.get('estimated_breach_year')}
- Years Until Quantum Threat: {hndl_data.get('years_until_threat')}
- Classical Security Bits: {hndl_data.get('classical_security_bits')}
- Current PQC Status: {pqc_data.get('pqc_status')}
- Vulnerability Reason: {pqc_data.get('vulnerability_reason')}
- Recommended Algorithm: {pqc_data.get('recommended_replacement', {}).get('algorithm', 'ML-KEM-768')}

Generate a detailed, actionable PQC migration plan specifically for PNB's banking infrastructure context.
Return ONLY valid JSON with no markdown, no explanation outside JSON:

{{
  "summary": "2-sentence executive summary specific to this asset and its banking context",
  "priority": "Immediate/High/Medium/Low",
  "effort_estimate": "Low/Medium/High",
  "estimated_timeline": "e.g. 3-6 months",
  "business_impact": "Impact on banking operations during migration",
  "replacement_algorithm": {{
    "name": "NIST FIPS algorithm name",
    "fips_standard": "FIPS 203/204/205",
    "oid": "algorithm OID dotted notation",
    "security_level": "NIST security level 1-5",
    "quantum_security_bits": "post-quantum security in bits"
  }},
  "migration_steps": [
    {{
      "step": 1,
      "title": "step title",
      "description": "detailed description tailored to banking context",
      "commands": ["relevant code/config examples"],
      "estimated_time": "time for this step",
      "dependencies": "what must be done first"
    }}
  ],
  "recommended_libraries": [
    {{
      "name": "library name",
      "language": "Python/Java/C/etc",
      "install": "install command",
      "purpose": "specific purpose for PNB's use case",
      "maturity": "Production-ready/Beta/Experimental"
    }}
  ],
  "risks": ["specific risk 1 for banking context", "specific risk 2"],
  "hybrid_approach": "Explain the classical+PQC hybrid strategy for safe transition",
  "testing_approach": "How to test the PQC migration without disrupting banking services",
  "rollback_plan": "How to rollback safely if migration causes issues",
  "compliance_notes": "CERT-IN / RBI / SEBI compliance considerations for Indian banking",
  "cert_in_alignment": "How this migration aligns with CERT-IN Annexure-A requirements",
  "cost_estimate": "Rough cost estimate for migration resources"
}}"""


def _fallback_plan(scan_data: dict, pqc_data: dict, hndl_data: dict) -> dict:
    """
    Structured fallback migration plan when Gemini API is unavailable.
    Provides real NIST PQC recommendations based on the asset's cipher suite.
    """
    hostname = scan_data.get("hostname", "asset")
    cipher = scan_data.get("cipher_suite", "")
    tls_version = scan_data.get("tls_version", "TLS 1.2")
    key_size = scan_data.get("cert_key_size", 2048)
    pqc_status = pqc_data.get("pqc_status", "Standard")
    breach_year = hndl_data.get("estimated_breach_year", 2033)
    years = hndl_data.get("years_until_threat", 7)
    replacement = pqc_data.get("recommended_replacement", {})

    priority = "High" if pqc_status in ["Critical", "Legacy"] else "Medium"
    timeline = "3-6 months" if pqc_status == "Critical" else "6-12 months"
    effort = "High" if pqc_status == "Critical" else "Medium"

    algo = replacement.get("algorithm", "ML-KEM-768")
    fips = replacement.get("fips", "FIPS 203")
    oid = replacement.get("oid", "2.16.840.1.101.3.4.4.2")

    plan = {
        "summary": (
            f"{hostname} uses {cipher} (TLS {tls_version}), which is quantum-vulnerable "
            f"with an estimated CRQC decryption risk by {breach_year} ({years} years). "
            f"Immediate migration to {algo} ({fips}) is required to protect PNB's banking data."
        ),
        "priority": priority,
        "effort_estimate": effort,
        "estimated_timeline": timeline,
        "business_impact": (
            "Planned maintenance window required for certificate replacement. "
            "Expect 30–60 minutes of TLS configuration downtime per server. "
            "Hybrid classical+PQC mode recommended during transition."
        ),
        "replacement_algorithm": {
            "name": algo,
            "fips_standard": fips,
            "oid": oid,
            "security_level": replacement.get("security_level", 3),
            "quantum_security_bits": "128 (NIST Level 3)"
        },
        "migration_steps": [
            {
                "step": 1,
                "title": "Cryptographic Inventory & Risk Assessment",
                "description": (
                    f"Document all systems using {cipher} at {hostname}. "
                    "Map dependencies, API consumers, and certificate trust chains. "
                    "Identify HSMs and load balancers that need firmware updates."
                ),
                "commands": [
                    f"# Scan all TLS endpoints",
                    f"openssl s_client -connect {hostname}:443 -showcerts 2>/dev/null",
                    f"# Check cipher negotiation",
                    f"nmap --script ssl-enum-ciphers -p 443 {hostname}"
                ],
                "estimated_time": "1-2 weeks",
                "dependencies": "None — first step"
            },
            {
                "step": 2,
                "title": "Install PQC Libraries and Development Environment",
                "description": (
                    f"Install liboqs (Open Quantum Safe) and OQS-Provider for OpenSSL. "
                    f"Configure {algo} cipher support in your TLS stack."
                ),
                "commands": [
                    "# Install liboqs",
                    "pip install liboqs-python",
                    "# Or for Java/BouncyCastle PQC",
                    "# <dependency>org.bouncycastle:bcpqc-jdk18on:1.78</dependency>",
                    f"# Python: generate {algo} keypair",
                    "import oqs",
                    f"with oqs.KeyEncapsulation('{algo}') as kem:",
                    "    public_key = kem.generate_keypair()",
                    "    ciphertext, shared_secret_enc = kem.encap_secret(public_key)"
                ],
                "estimated_time": "1 week",
                "dependencies": "Step 1 completed"
            },
            {
                "step": 3,
                "title": "Implement Hybrid Classical + PQC Mode",
                "description": (
                    f"Deploy hybrid TLS: classical ECDHE + {algo} simultaneously. "
                    "This ensures backwards compatibility while adding quantum protection. "
                    "Both algorithms must be compromised for the key exchange to fail."
                ),
                "commands": [
                    "# Nginx hybrid PQC configuration",
                    "ssl_protocols TLSv1.3;",
                    f"# Enable hybrid groups in OpenSSL with OQS-Provider",
                    "ssl_ecdh_curve X25519MLKEM768:prime256v1:secp384r1;",
                    "ssl_prefer_server_ciphers off;"
                ],
                "estimated_time": "2-4 weeks",
                "dependencies": "Step 2 completed, test environment ready"
            },
            {
                "step": 4,
                "title": "Certificate Renewal with PQC Signature",
                "description": (
                    f"Request new X.509 certificates with ML-DSA-65 (FIPS 204) signatures "
                    f"from a PQC-capable CA. Update certificate pinning in mobile apps."
                ),
                "commands": [
                    "# Generate ML-DSA-65 certificate signing request",
                    "openssl genpkey -algorithm ML-DSA-65 -out pqc_private.pem",
                    "openssl req -new -key pqc_private.pem -out pqc_csr.pem",
                    "# Submit to Let's Encrypt / DigiCert PQC CA"
                ],
                "estimated_time": "2-3 weeks",
                "dependencies": "CA support for PQC signatures (check with DigiCert/Entrust)"
            },
            {
                "step": 5,
                "title": "Testing, Validation & Monitoring",
                "description": (
                    "Perform comprehensive load testing with PQC enabled. "
                    "Validate HNDL risk mitigation. Update CBOM in QuantumSight. "
                    "Set up monitoring for PQC algorithm negotiation rates."
                ),
                "commands": [
                    "# Test PQC handshake",
                    f"openssl s_client -connect {hostname}:443 -groups X25519MLKEM768",
                    "# Verify cipher negotiation",
                    "openssl s_client -connect {hostname}:443 2>&1 | grep 'Cipher'",
                    "# Load test",
                    "ab -n 10000 -c 100 https://{hostname}/"
                ],
                "estimated_time": "1-2 weeks",
                "dependencies": "Steps 1-4 completed"
            }
        ],
        "recommended_libraries": [
            {
                "name": "liboqs-python",
                "language": "Python",
                "install": "pip install liboqs-python",
                "purpose": f"Open Quantum Safe library — implements {algo} and all NIST PQC algorithms",
                "maturity": "Production-ready"
            },
            {
                "name": "OQS-Provider",
                "language": "C/OpenSSL",
                "install": "Build from source: github.com/open-quantum-safe/oqs-provider",
                "purpose": "OpenSSL provider for PQC algorithms in TLS",
                "maturity": "Production-ready"
            },
            {
                "name": "BouncyCastle PQC",
                "language": "Java",
                "install": "<dependency>org.bouncycastle:bcpqc-jdk18on:1.78</dependency>",
                "purpose": "Java PQC library for banking middleware and backend services",
                "maturity": "Production-ready"
            },
            {
                "name": "pqcrypto",
                "language": "Python",
                "install": "pip install pqcrypto",
                "purpose": "Pure Python PQC implementations for prototyping",
                "maturity": "Beta"
            }
        ],
        "risks": [
            f"Performance overhead: {algo} key generation is ~10x slower than RSA-2048. "
            "Profile carefully on high-traffic banking endpoints.",
            "CA ecosystem: Most commercial CAs do not yet issue PQC-signed certificates. "
            "Plan for self-signed or Let's Encrypt pilot programmes.",
            "Client compatibility: Older browsers and banking apps may not support PQC. "
            "Hybrid mode essential during transition period.",
            "HSM support: Hardware Security Modules may require firmware upgrades to "
            "support PQC operations. Verify with Thales/nCipher/SafeNet vendors.",
            "Regulatory approval: Confirm CERT-IN and RBI accept NIST FIPS 203/204/205 "
            "before production deployment."
        ],
        "hybrid_approach": (
            f"Deploy classical ECDHE-P256 + {algo} simultaneously in TLS 1.3. "
            "The combined shared secret is derived from both algorithms using HKDF. "
            "If either algorithm is broken, the connection remains secure from the other. "
            "This provides quantum protection while maintaining compatibility with "
            "non-PQC clients. Use OpenSSL with OQS-Provider: 'X25519MLKEM768' hybrid group."
        ),
        "testing_approach": (
            "1. Unit test PQC key generation and encapsulation/decapsulation. "
            "2. Integration test: full TLS handshake with hybrid mode enabled. "
            "3. Compatibility test: verify existing API clients can connect. "
            "4. Performance test: measure latency increase vs RSA baseline (expect <5ms overhead). "
            "5. Security validation: use QuantumSight to re-scan and verify PQC tier upgrade. "
            "6. Canary deployment: 5% traffic to PQC-enabled servers before full rollout."
        ),
        "rollback_plan": (
            "Maintain RSA certificates in parallel during transition. "
            "If PQC causes client compatibility issues, disable via nginx config change: "
            "revert 'ssl_ecdh_curve' to 'prime256v1' — no code deployment required. "
            "Full rollback achievable within 5 minutes via load balancer configuration."
        ),
        "compliance_notes": (
            "CERT-IN Annexure-A: This migration brings the asset into full compliance "
            "with CERT-IN's cryptographic inventory and PQC readiness requirements. "
            "RBI IT Framework: Aligns with Section 7.4 (Cryptographic Controls) — "
            "ensures banking data encryption meets post-2030 threat model requirements. "
            "NPCI PCI-DSS: PQC migration supports PCI-DSS 4.0 cryptographic agility requirements."
        ),
        "cert_in_alignment": (
            f"Post-migration CBOM entry will reflect: "
            f"Algorithm='{algo}', Primitive='kem', FIPS='{fips}', "
            f"ClassicalSecurityLevel='128 (quantum-safe)', "
            f"PQCStatus='Elite-PQC', HNDLRisk='SAFE'. "
            "Fully compliant with CERT-IN Annexure-A CBOM field requirements."
        ),
        "cost_estimate": (
            "Development: 2-3 engineers × 2-3 months = ₹15-25 lakh. "
            "Infrastructure: Minimal — software-only change, no hardware required. "
            "CA/Certificates: ₹50,000-2,00,000 for PQC-capable CA subscription. "
            "Testing/Security review: ₹5-10 lakh for external PQC audit."
        ),
        "generated_at": datetime.now().isoformat(),
        "hostname": hostname,
        "ai_model": "template-v1 (Gemini API key not configured)",
        "ai_generated": False
    }

    return {"success": True, "plan": plan}
