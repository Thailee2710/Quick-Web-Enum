"""Compatibility helpers for the historical rpchecker module."""

from __future__ import annotations

import asyncio

from quick_web_enum.core import build_probe_urls, probe_url


def site_is_online(url: str, timeout: float = 2) -> bool:
    """Return True if any HTTP(S) probe for *url* returns a response."""

    error: Exception = Exception("unknown error")
    for probe in build_probe_urls(url):
        finding = probe_url(probe, timeout=timeout)
        if finding.status is not None:
            return True
        error = Exception(finding.error or "offline")
    raise error


async def site_is_online_async(url: str, timeout: float = 2) -> bool:
    """Async wrapper around :func:`site_is_online` for legacy callers."""

    return await asyncio.to_thread(site_is_online, url, timeout)
