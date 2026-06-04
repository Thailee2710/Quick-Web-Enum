"""Command line interface for Quick Web Enum."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import (
    DEFAULT_PORTS,
    build_probe_urls,
    enumerate_paths,
    parse_ports,
    probe_url,
    read_lines,
    resolve_host,
    reverse_dns,
    safe_output_name,
    scan_ports,
    write_findings_csv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quick-web-enum",
        description="Safe, modern baseline web enumeration toolkit for authorized targets.",
    )
    parser.add_argument("--version", action="version", version="Quick-Web-Enum 2.0.0")
    subcommands = parser.add_subparsers(dest="command", required=True)

    check = subcommands.add_parser("check", help="Probe HTTP(S) availability for targets")
    _add_target_args(check)
    check.add_argument("--timeout", type=float, default=5.0)
    check.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    check.set_defaults(func=cmd_check)

    resolve = subcommands.add_parser("resolve", help="Resolve hostnames and reverse DNS")
    _add_target_args(resolve)
    resolve.set_defaults(func=cmd_resolve)

    ports = subcommands.add_parser("ports", help="TCP connect scan explicit ports")
    _add_target_args(ports)
    ports.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS), help="Ports/ranges, e.g. 80,443,8000-8010")
    ports.add_argument("--timeout", type=float, default=2.0)
    ports.set_defaults(func=cmd_ports)

    paths = subcommands.add_parser("paths", help="Probe common web paths from a wordlist")
    _add_target_args(paths)
    paths.add_argument("-w", "--wordlist", default="common.txt", help="Path wordlist")
    paths.add_argument("-o", "--output-dir", default="output/endpoints", help="Directory for CSV reports")
    paths.add_argument("--timeout", type=float, default=5.0)
    paths.add_argument("--insecure", action="store_true", help="Disable TLS certificate verification")
    paths.add_argument("--statuses", default="200,204,301,302,307,308,401,403", help="Interesting HTTP statuses")
    paths.set_defaults(func=cmd_paths)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


def cmd_check(args: argparse.Namespace) -> int:
    for target in _targets_from_args(args):
        for url in build_probe_urls(target):
            finding = probe_url(url, timeout=args.timeout, verify_tls=not args.insecure)
            status = finding.status if finding.status is not None else "ERR"
            detail = finding.title or finding.error
            print(f"{status}\t{finding.size}\t{finding.content_type}\t{url}\t{detail}".rstrip())
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    failed = False
    for target in _targets_from_args(args):
        host = target.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
        try:
            addresses = resolve_host(host)
        except OSError as exc:
            print(f"ERR\t{host}\t{exc}", file=sys.stderr)
            failed = True
            continue
        for address in addresses:
            ptr = reverse_dns(address) or ""
            print(f"{host}\t{address}\t{ptr}".rstrip())
    return 1 if failed else 0


def cmd_ports(args: argparse.Namespace) -> int:
    ports = parse_ports(args.ports)
    for target in _targets_from_args(args):
        host = target.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]
        open_ports = scan_ports(host, ports=ports, timeout=args.timeout)
        if open_ports:
            for port in open_ports:
                print(f"{host}:{port}")
        else:
            print(f"{host}\tno open ports in requested set")
    return 0


def cmd_paths(args: argparse.Namespace) -> int:
    words = read_lines(args.wordlist)
    statuses = {int(item.strip()) for item in args.statuses.split(",") if item.strip()}
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_findings = []
    for target in _targets_from_args(args):
        findings = enumerate_paths(
            target,
            words,
            timeout=args.timeout,
            verify_tls=not args.insecure,
            include_statuses=statuses,
        )
        all_findings.extend(findings)
        output_path = output_dir / f"{safe_output_name(target)}.csv"
        write_findings_csv(output_path, findings)
        print(f"{target}\t{len(findings)} findings\t{output_path}")

    summary_path = output_dir / "summary.csv"
    write_findings_csv(summary_path, all_findings)
    return 0


def _add_target_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("targets", nargs="*", help="Targets (hosts, IPs, host:port, or URLs)")
    parser.add_argument("-f", "--input-file", help="Read targets from file")


def _targets_from_args(args: argparse.Namespace) -> list[str]:
    targets = list(args.targets)
    if args.input_file:
        targets.extend(read_lines(args.input_file))
    if not targets:
        raise SystemExit("at least one target or --input-file is required")
    return targets


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
