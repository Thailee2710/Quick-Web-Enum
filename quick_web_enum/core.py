"""Core helpers for Quick Web Enum.

The functions in this module avoid shell execution by default so they are safe to
unit-test and to reuse from the CLI. Heavy external scanners such as nmap,
masscan, ffuf, and dirsearch can still be orchestrated by users separately, but
this package now provides a dependable standard-library baseline.
"""

from __future__ import annotations

import csv
import ipaddress
import re
import socket
import ssl
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

DEFAULT_PORTS = (80, 443, 8080, 8443, 8000, 3000, 5000, 9000)
_HTTP_PORTS = {80, 8080, 8000, 3000, 5000, 9000}
_HTTPS_PORTS = {443, 8443}


@dataclass(frozen=True)
class Target:
    """Normalized network target."""

    raw: str
    host: str
    scheme: str | None = None
    port: int | None = None
    path: str = "/"

    @property
    def hostport(self) -> str:
        return f"{self.host}:{self.port}" if self.port else self.host


@dataclass(frozen=True)
class EndpointFinding:
    """Result from probing a web endpoint."""

    url: str
    status: int | None
    size: int
    content_type: str
    title: str = ""
    error: str = ""

    def to_csv_row(self) -> list[str]:
        return [
            self.url,
            "" if self.status is None else str(self.status),
            str(self.size),
            self.content_type,
            self.title or self.error,
        ]


def read_lines(path: str | Path) -> list[str]:
    """Read non-empty, non-comment lines from a text file."""

    with Path(path).expanduser().open(encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.lstrip().startswith("#")]


def normalize_target(value: str) -> Target:
    """Normalize host/IP/URL input into a Target object.

    Accepted examples: ``example.com``, ``10.0.0.1:8080``,
    ``https://example.com/admin``. Raises ValueError for empty or invalid ports.
    """

    raw = value.strip()
    if not raw:
        raise ValueError("empty target")

    candidate = raw if "://" in raw else f"//{raw}"
    parsed = urlparse(candidate)
    host = parsed.hostname
    if not host:
        raise ValueError(f"invalid target: {value!r}")

    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"invalid port in target: {value!r}") from exc

    scheme = parsed.scheme or None
    path = parsed.path or "/"
    return Target(raw=raw, host=host, scheme=scheme, port=port, path=path)


def is_ip_address(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def resolve_host(host: str) -> list[str]:
    """Resolve a hostname to unique IPv4/IPv6 addresses."""

    infos = socket.getaddrinfo(host, None)
    addresses: list[str] = []
    for info in infos:
        address = info[4][0]
        if address not in addresses:
            addresses.append(address)
    return addresses


def reverse_dns(address: str) -> str | None:
    try:
        return socket.gethostbyaddr(address)[0]
    except (OSError, socket.herror):
        return None


def check_tcp_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Return True when a TCP connection can be opened."""

    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return True
    except OSError:
        return False


def scan_ports(host: str, ports: Iterable[int] = DEFAULT_PORTS, timeout: float = 2.0) -> list[int]:
    """Scan a small explicit port list using TCP connect."""

    open_ports: list[int] = []
    for port in ports:
        if check_tcp_port(host, int(port), timeout=timeout):
            open_ports.append(int(port))
    return open_ports


def build_probe_urls(target: str | Target) -> list[str]:
    """Build HTTP(S) URLs to probe for a host/IP/URL target."""

    normalized = normalize_target(target) if isinstance(target, str) else target
    path = normalized.path if normalized.path.startswith("/") else f"/{normalized.path}"

    if normalized.scheme:
        return [_format_url(normalized.scheme, normalized.host, normalized.port, path)]

    if normalized.port in _HTTPS_PORTS:
        schemes = ("https", "http")
    elif normalized.port in _HTTP_PORTS:
        schemes = ("http", "https")
    elif normalized.port:
        schemes = ("https", "http")
    else:
        schemes = ("http", "https")

    return [_format_url(scheme, normalized.host, normalized.port, path) for scheme in schemes]


def probe_url(url: str, timeout: float = 5.0, verify_tls: bool = True) -> EndpointFinding:
    """Fetch a URL with a lightweight GET request and return a finding."""

    request = Request(url, headers={"User-Agent": "Quick-Web-Enum/2.0"}, method="GET")
    context = None
    if url.startswith("https://") and not verify_tls:
        context = ssl._create_unverified_context()  # nosec B323

    try:
        with urlopen(request, timeout=timeout, context=context) as response:  # nosec B310
            body = response.read(1_000_000)
            content_type = response.headers.get("Content-Type", "")
            return EndpointFinding(
                url=url,
                status=response.status,
                size=len(body),
                content_type=content_type,
                title=_extract_title(body),
            )
    except HTTPError as exc:
        body = exc.read(1_000_000)
        return EndpointFinding(
            url=url,
            status=exc.code,
            size=len(body),
            content_type=exc.headers.get("Content-Type", ""),
            title=_extract_title(body),
        )
    except (URLError, TimeoutError, OSError, ValueError, ssl.SSLError) as exc:
        return EndpointFinding(url=url, status=None, size=0, content_type="", error=str(exc))


def enumerate_paths(
    base_target: str,
    words: Iterable[str],
    timeout: float = 5.0,
    verify_tls: bool = True,
    include_statuses: set[int] | None = None,
) -> list[EndpointFinding]:
    """Probe common paths for one target.

    ``include_statuses`` defaults to common useful statuses for discovery.
    """

    include_statuses = include_statuses or {200, 204, 301, 302, 307, 308, 401, 403}
    findings: list[EndpointFinding] = []
    for base in build_probe_urls(base_target):
        root = base.rstrip("/")
        for word in words:
            clean_word = word.strip().split()[0].lstrip("/") if word.strip() else ""
            if not clean_word:
                continue
            encoded_word = quote(clean_word, safe="/%:@")
            finding = probe_url(f"{root}/{encoded_word}", timeout=timeout, verify_tls=verify_tls)
            if finding.status in include_statuses:
                findings.append(finding)
    return findings


def write_findings_csv(path: str | Path, findings: Iterable[EndpointFinding]) -> None:
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["url", "status", "size", "content_type", "title_or_error"])
        for finding in findings:
            writer.writerow(finding.to_csv_row())


def safe_output_name(value: str) -> str:
    """Make a stable filename fragment from a URL/host."""

    value = value.strip().replace("://", "_")
    value = re.sub(r"[\\/\s:]+", "_", value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = value.strip("._-")
    while ".." in value:
        value = value.replace("..", ".")
    return value or "target"


def parse_ports(value: str) -> list[int]:
    """Parse ports like ``80,443,8000-8003``."""

    ports: list[int] = []
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start, end = int(start_s), int(end_s)
            if start > end:
                raise ValueError(f"invalid port range: {chunk}")
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(chunk))
    for port in ports:
        if not 1 <= port <= 65535:
            raise ValueError(f"invalid port: {port}")
    return sorted(dict.fromkeys(ports))


def parse_open_port_line(line: str) -> tuple[str, int] | None:
    """Parse common ``host:port`` and masscan output lines."""

    line = line.strip()
    host_port = re.match(r"^([A-Za-z0-9_.:-]+):(\d{1,5})$", line)
    if host_port:
        return host_port.group(1), int(host_port.group(2))

    masscan = re.search(r"open port\s+(\d{1,5})/tcp\s+on\s+([A-Za-z0-9_.:-]+)", line, re.IGNORECASE)
    if masscan:
        return masscan.group(2), int(masscan.group(1))
    return None


def _format_url(scheme: str, host: str, port: int | None, path: str) -> str:
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    port_part = "" if port is None or default_port else f":{port}"
    return f"{scheme}://{host}{port_part}{path}"


def _extract_title(body: bytes) -> str:
    text = body[:50_000].decode("utf-8", errors="ignore")
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()[:200]


def _looks_ipv4(host: str) -> bool:
    try:
        return isinstance(ipaddress.ip_address(host), ipaddress.IPv4Address)
    except ValueError:
        return False
