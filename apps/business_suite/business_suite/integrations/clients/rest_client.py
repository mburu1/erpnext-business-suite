"""Configuration-driven REST transport with bounded retries."""

from __future__ import annotations

import time
from typing import Any

import requests


class RestClient:
    """HTTP client with explicit timeouts, bounded retries and no secret logging."""

    RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}

    def __init__(
        self,
        base_url: str,
        timeout: tuple[float, float] = (5.0, 30.0),
        max_retries: int = 2,
        backoff_seconds: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max(0, min(int(max_retries), 5))
        self.backoff_seconds = max(float(backoff_seconds), 0.0)

    def request(self, method: str, path: str, *, headers=None, params=None, json=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        last_response = None

        for attempt in range(self.max_retries + 1):
            started = time.perf_counter()
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=headers or {},
                    params=params,
                    json=json,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise
                time.sleep(self.backoff_seconds * (2**attempt))
                last_response = exc
                continue

            duration_ms = int((time.perf_counter() - started) * 1000)
            if response.status_code in self.RETRYABLE_STATUS_CODES and attempt < self.max_retries:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = min(float(retry_after), 30.0) if retry_after else self.backoff_seconds * (2**attempt)
                except ValueError:
                    delay = self.backoff_seconds * (2**attempt)
                time.sleep(max(delay, 0.0))
                last_response = response
                continue

            try:
                payload: Any = response.json()
            except ValueError:
                payload = response.text

            return response.status_code, payload, duration_ms

        if isinstance(last_response, requests.Response):
            return last_response.status_code, last_response.text, 0
        raise RuntimeError("REST request exhausted without a response")
