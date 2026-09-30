"""Run deterministic repository and optional live HTTP validation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "apps/business_suite/business_suite/tests/test_e2e_contracts.py",
    ]

    env = os.environ.copy()
    result = subprocess.run(command, cwd=ROOT, env=env, check=False)

    if result.returncode != 0:
        return result.returncode

    if env.get("BUSINESS_SUITE_BASE_URL"):
        print("Live Business Suite E2E checks were enabled.")
    else:
        print(
            "Live Business Suite E2E checks were skipped. "
            "Set BUSINESS_SUITE_BASE_URL to enable them."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
