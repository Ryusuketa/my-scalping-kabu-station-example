"""Authentication client for kabu station API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import requests


@dataclass
class AuthClient:
    base_url: str
    timeout_seconds: float = 5.0

    def fetch_token(self, api_password: str) -> str:
        payload = {"APIPassword": api_password}
        response = requests.post(
            f"{self.base_url}/token",
            json=payload,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        data: Mapping[str, Any] = response.json()
        token = data.get("Token")
        if not token:
            raise ValueError("Token missing from auth response")
        return str(token)
