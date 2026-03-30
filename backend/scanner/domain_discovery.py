"""
Domain Discovery — DNS enumeration and subdomain discovery.
Uses dnspython to enumerate DNS records and discover public-facing
subdomains, A records, AAAA records, MX, NS, and CNAME records.
"""
import asyncio
import logging
import socket
from typing import Optional

try:
    import dns.resolver
    import dns.asyncresolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Common subdomain prefixes to enumerate
COMMON_SUBDOMAINS = [
    "www", "mail", "vpn", "api", "portal", "netbanking", "mobileapi",
    "payments", "mobile", "app", "secure", "login", "auth", "admin",
    "gateway", "cdn", "static", "assets", "img", "media", "dev",
    "staging", "test", "uat", "preprod", "legacy", "old", "new",
    "webmail", "smtp", "imap", "pop", "ns1", "ns2", "ftp", "sftp",
    "ssh", "remote", "vpn2", "vpn3", "sso", "idp", "oidc", "oauth",
    "reporting", "analytics", "dashboard", "monitoring", "alerts",
    "support", "helpdesk", "kb", "docs", "status", "health",
]


async def discover_domains(base_domain: str) -> dict:
    """
    Discover all subdomains and DNS records for a base domain.
    Returns discovered hostnames with their IP addresses.
    """
    results = {
        "base_domain": base_domain,
        "subdomains": [],
        "a_records": [],
        "aaaa_records": [],
        "mx_records": [],
        "ns_records": [],
        "cname_records": [],
        "discovered_hosts": []
    }

    # Resolve base domain
    base_ips = await _resolve_a(base_domain)
    if base_ips:
        results["a_records"] = base_ips
        results["discovered_hosts"].append({
            "hostname": base_domain,
            "ip": base_ips[0] if base_ips else None,
            "is_subdomain": False
        })

    # Get NS records
    ns_records = await _resolve_ns(base_domain)
    results["ns_records"] = ns_records

    # Enumerate common subdomains concurrently
    tasks = []
    for sub in COMMON_SUBDOMAINS:
        hostname = f"{sub}.{base_domain}"
        tasks.append(_check_subdomain(hostname))

    subdomain_results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in subdomain_results:
        if isinstance(result, dict) and result.get("exists"):
            results["subdomains"].append(result["hostname"])
            results["discovered_hosts"].append({
                "hostname": result["hostname"],
                "ip": result["ip"],
                "ipv6": result.get("ipv6"),
                "is_subdomain": True
            })

    return results


async def _check_subdomain(hostname: str) -> dict:
    """Check if a subdomain exists by resolving its A record."""
    try:
        loop = asyncio.get_event_loop()
        ips = await loop.run_in_executor(None, _sync_resolve_a, hostname)
        if ips:
            ipv6 = None
            try:
                ipv6_list = await loop.run_in_executor(None, _sync_resolve_aaaa, hostname)
                ipv6 = ipv6_list[0] if ipv6_list else None
            except Exception:
                pass
            return {"hostname": hostname, "ip": ips[0], "ipv6": ipv6, "exists": True}
    except Exception:
        pass
    return {"hostname": hostname, "exists": False}


async def _resolve_a(hostname: str) -> list:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_resolve_a, hostname)


async def _resolve_ns(hostname: str) -> list:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_resolve_ns, hostname)


def _sync_resolve_a(hostname: str) -> list:
    try:
        if DNS_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            answers = resolver.resolve(hostname, 'A')
            return [str(r) for r in answers]
        else:
            infos = socket.getaddrinfo(hostname, None, socket.AF_INET)
            return list({info[4][0] for info in infos})
    except Exception:
        return []


def _sync_resolve_aaaa(hostname: str) -> list:
    try:
        if DNS_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            answers = resolver.resolve(hostname, 'AAAA')
            return [str(r) for r in answers]
        else:
            infos = socket.getaddrinfo(hostname, None, socket.AF_INET6)
            return list({info[4][0] for info in infos})
    except Exception:
        return []


def _sync_resolve_ns(hostname: str) -> list:
    try:
        if DNS_AVAILABLE:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            answers = resolver.resolve(hostname, 'NS')
            return [str(r) for r in answers]
    except Exception:
        pass
    return []
