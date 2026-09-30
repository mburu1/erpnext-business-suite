"""Small, configuration-driven REST client for external integrations."""

from __future__ import annotations

import time
from typing import Any

import requests


class RestClient:
    """HTTP client with explicit timeouts and no secret persistence."""

    def __init__(self, base_url: str, timeout: tuple[float, float] = (5.0, 30.0)):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request(self, method: str, path: str, *, headers=None, params=None, json=None):
        started = time.perf_counter()
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers or {},
            params=params,
            json=json,
            timeout=self.timeout,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        try:
            payload: Any = response.json()
        except ValueError:
            payload = response.text
        return response.status_code, payload, duration_ms
