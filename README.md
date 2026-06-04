# Quick Web Enum

Quick Web Enum is a lightweight command-line toolkit for **authorized** web reconnaissance. It started as a helper script for scanning ports, probing HTTP/HTTPS endpoints, and checking DNS. Version 2 modernizes the project into a safer Python package with a test suite, predictable CLI commands, and no required runtime dependencies.

> Use this only on systems you own or have explicit permission to assess.

## What's new in v2

- Replaced the old interactive menu with an `argparse` CLI.
- Removed unsafe `shell=True` command construction for the built-in scanner.
- Removed unnecessary runtime dependencies (`numpy`, `configparser`).
- Added installable console scripts: `quick-web-enum` and `qwc`.
- Added unit tests for parsing, URL generation, safe output names, and CSV serialization.
- Added `.gitignore`, `pyproject.toml`, and modern packaging metadata.
- Kept `python qwc.py ...` as a backward-compatible launcher.

## Install

### From source

```bash
git clone https://github.com/Thailee2710/Quick-Web-Enum.git
cd Quick-Web-Enum
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For development tools:

```bash
python -m pip install -e '.[dev]'
```

If you use `uv`:

```bash
uv venv
uv pip install -e '.[dev]'
```

## Commands

### Check HTTP/HTTPS availability

```bash
quick-web-enum check example.com 10.0.0.1:8080 https://example.com/admin
```

Output format:

```text
status size content-type url title-or-error
```

### Resolve DNS and reverse DNS

```bash
quick-web-enum resolve example.com 8.8.8.8
```

### Scan explicit TCP ports

The built-in port scanner is a conservative TCP connect scanner. It is not a replacement for `masscan`, but it is safe and dependency-free for quick checks.

```bash
quick-web-enum ports example.com --ports 80,443,8000-8010 --timeout 1
```

### Probe common paths

```bash
quick-web-enum paths example.com -w common.txt -o output/endpoints
```

This writes one CSV per target and a combined `summary.csv`.

### Read targets from a file

```bash
quick-web-enum check -f input/ipNoPort.txt
quick-web-enum paths -f output/domain.txt -w common.txt -o output/endpoints
```

## Backward compatibility

The old entrypoint still works, but now expects subcommands:

```bash
python qwc.py check example.com
python qwc.py paths example.com -w common.txt
```

## Suggested external workflow

Quick Web Enum now provides a safe baseline. For deeper authorized assessments, combine it with specialist tools:

- `nmap` for detailed service/version detection.
- `masscan` for large-scale high-speed port discovery.
- `ffuf` or `dirsearch` for aggressive content discovery.

Example handoff:

```bash
quick-web-enum ports example.com --ports 80,443,8080,8443
quick-web-enum paths example.com -w common.txt -o output/endpoints
nmap -sV -Pn -p 80,443 example.com
```

## Development

Run tests:

```bash
python -m pytest
```

Run lint:

```bash
ruff check .
```

Run a security sanity scan:

```bash
bandit -q -r quick_web_enum qwc.py
```

## Repository layout

```text
quick_web_enum/     Modern package and CLI
tests/              Unit tests
qwc.py              Backward-compatible launcher
common.txt          Small sample wordlist
input/              Example input files
output/             Runtime output directory placeholder
```

## License

MIT. See [LICENSE](LICENSE).
