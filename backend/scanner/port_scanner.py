"""
Port Scanner — Scans common banking/TLS ports on discovered hosts.
Checks ports 80, 443, 8443, 8080 to discover web-facing services.
"""
import asyncio
import socket
import logging
from typing import Optional

logger = logging.getLogger(__name__)

BANKING_PORTS = [80, 443, 8443, 8080, 4443, 9443]


async def scan_ports(hostname: str, ports: list = None) -> dict:
    """
    Scan specified ports on a hostname.
    Returns open ports with detected service types.
    """
    if ports is None:
        ports = BANKING_PORTS

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, _check_port, hostname, port)
        for port in ports
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    open_ports = []
    for result in results:
        if isinstance(result, dict) and result.get("open"):
            open_ports.append(result)

    return {
        "hostname": hostname,
        "open_ports": open_ports,
        "port_count": len(open_ports)
    }


def _check_port(hostname: str, port: int) -> dict:
    try:
        with socket.create_connection((hostname, port), timeout=5):
            service = _detect_service(port)
            return {"port": port, "open": True, "service": service}
    except Exception:
        return {"port": port, "open": False}


def _detect_service(port: int) -> str:
    services = {
        80: "HTTP",
        443: "HTTPS/TLS",
        8443: "HTTPS-Alt/TLS",
        8080: "HTTP-Alt",
        4443: "HTTPS-Alt",
        9443: "HTTPS-Alt"
    }
    return services.get(port, "Unknown")
