"""Legacy CLI helpers for RP Checker."""

from __future__ import annotations

import argparse


def read_user_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="rpchecker", description="check the availability of websites"
    )
    parser.add_argument("-u", "--urls", metavar="URLs", nargs="+", default=[], help="one or more URLs")
    parser.add_argument("-f", "--input-file", metavar="FILE", default="", help="read URLs from a file")
    parser.add_argument("-a", "--asynchronous", action="store_true", help="run checks concurrently")
    return parser.parse_args()


def display_check_result(result: bool, url: str, error: str = "") -> None:
    # Preserve old machine-readable output: 1 online, 2 offline.
    print("1" if result else "2")
