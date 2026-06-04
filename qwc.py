"""Backward-compatible launcher for the modern Quick Web Enum CLI."""

from quick_web_enum.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
