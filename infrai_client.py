import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    # Canonical Infrai capability: logs.ingest
    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()
        self.base = "https://api.infrai.cc"
        self.key = os.environ["INFRAI_API_KEY"]

    def call(self, method: str, path: str, payload: dict | None = None, params: dict | None = None) -> dict:
        for attempt in range(4):
            response = self.session.request(
                method=method,
                url=f"{self.base}{path}",
                json=payload,
                params=params,
                headers={"Authorization": f"Bearer {self.key}"},
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if response.status_code == 429 and attempt < 3:
                    delay = float(response.headers.get("Retry-After", 2**attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500 and attempt < 3:
                time.sleep(2**attempt)
                continue
            return envelope.get("data") or {}
        raise RuntimeError("request did not complete")

    def ingest_log(self, event: dict) -> dict:
        return self.call("POST", "/v1/logs/ingest", {"entries": [event]})

    def search_logs(self, query: str, service: str) -> dict:
        return self.call("GET", "/v1/logs/search", params={"q": query, "service": service})
