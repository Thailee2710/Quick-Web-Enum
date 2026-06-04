
from quick_web_enum.core import (
    EndpointFinding,
    build_probe_urls,
    normalize_target,
    parse_open_port_line,
    safe_output_name,
)


def test_normalize_target_accepts_hosts_ips_and_urls():
    assert normalize_target("https://example.com/admin").host == "example.com"
    assert normalize_target("https://example.com/admin").scheme == "https"
    assert normalize_target("10.0.0.1:8080").host == "10.0.0.1"
    assert normalize_target("10.0.0.1:8080").port == 8080


def test_build_probe_urls_prefers_explicit_scheme_and_port():
    assert build_probe_urls("https://example.com") == ["https://example.com/"]
    assert build_probe_urls("example.com:8443") == ["https://example.com:8443/", "http://example.com:8443/"]
    assert build_probe_urls("example.com") == ["http://example.com/", "https://example.com/"]


def test_safe_output_name_removes_path_separators_and_odd_chars():
    assert safe_output_name("https://example.com:8443/api/v1") == "https_example.com_8443_api_v1"
    assert ".." not in safe_output_name("../../etc/passwd")


def test_parse_open_port_line_supports_legacy_masscan_and_modern_formats():
    assert parse_open_port_line("Discovered open port 443/tcp on 10.0.0.1") == ("10.0.0.1", 443)
    assert parse_open_port_line("10.0.0.1:8080") == ("10.0.0.1", 8080)
    assert parse_open_port_line("not a port") is None


def test_endpoint_finding_serializes_to_csv_row():
    row = EndpointFinding("https://example.com/admin", 200, 123, "text/html", "OK").to_csv_row()
    assert row == ["https://example.com/admin", "200", "123", "text/html", "OK"]
