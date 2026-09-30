#!/usr/bin/env python3
"""Collect a small, secret-safe Frappe diagnostic bundle.

The script is intentionally read-only. It records command output that is useful
for support triage while redacting common credential/token patterns.

Run from a Frappe bench host, for example:
    python3 scripts/troubleshooting/collect_diagnostics.py --site mysite.local

The script does not execute database writes, migrations, queue clearing, or
service restarts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
from pathlib import Path


SECRET_PATTERNS = [
    (re.compile(r"(?i)(authorization\\s*[:=]\\s*bearer\\s+)[^\\s]+"), r"\\1[REDACTED]"),
    (re.compile(r"(?i)(bearer\\s+)[A-Za-z0-9._~+/=-]+"), r"\\1[REDACTED]"),
    (re.compile(r"(?i)(api[_-]?key\\s*[:=]\\s*)[^\\s,;]+"), r"\\1[REDACTED]"),
    (re.compile(r"(?i)(secret\\s*[:=]\\s*)[^\\s,;]+"), r"\\1[REDACTED]"),
    (re.compile(r"(?i)(password\\s*[:=]\\s*)[^\\s,;]+"), r"\\1[REDACTED]"),
    (re.compile(r"(?i)(token\\s*[:=]\\s*)[^\\s,;]+"), r"\\1[REDACTED]"),
]


def redact(text: str) -> str:
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def run(command: list[str], cwd: Path) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"[command unavailable/timeout: {exc}]"
    return redact(completed.stdout[-12000:])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", required=True, help="Frappe site name")
    parser.add_argument(
        "--output",
        default="diagnostics",
        help="Directory for the diagnostic bundle (default: diagnostics)",
    )
    args = parser.parse_args()

    bench = Path.cwd()
    output_root = Path(args.output)
    output_root.mkdir(parents=True, exist_ok=True)

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_root / f"frappe-diagnostics-{timestamp}.txt"

    commands = [
        ("git status", ["git", "status", "--short"]),
        ("git commit", ["git", "rev-parse", "HEAD"]),
        ("bench version", ["bench", "--site", args.site, "version"]),
        ("bench status", ["bench", "--site", args.site, "status"]),
        ("bench doctor", ["bench", "--site", args.site, "doctor"]),
        ("bench pending jobs", ["bench", "--site", args.site, "show-pending-jobs"]),
    ]

    lines = [
        "ERPNext Business Suite diagnostic bundle",
        f"Generated UTC: {dt.datetime.now(dt.timezone.utc).isoformat()}",
        f"Site: {args.site}",
        f"Working directory: {bench}",
        "Read-only collector: yes",
        "",
    ]

    for title, command in commands:
        lines.extend([f"## {title}", f"$ {' '.join(command)}", run(command, bench), ""])

    output.write_text("\\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
