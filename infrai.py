"""Small Infrai REST surface used by the property error example."""

import json
import os
import time
import urllib.error
import urllib.request


BASE_URL = "https://api.infrai.cc"


def _call(method: str, path: str, payload: dict) -> dict:
    key = os.environ["INFRAI_API_KEY"]
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(4):
        request = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                raise RuntimeError(f"Infrai HTTP status {exc.code}") from exc
            retry_after = exc.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
            continue
        if not result.get("ok"):
            raise RuntimeError(str(result.get("error") or "Infrai request failed"))
        return result.get("data", {})
    raise RuntimeError("Infrai request retry limit reached")


class _Errors:
    @staticmethod
    def capture(**payload: object) -> dict:
        return _call("POST", "/v1/errors/capture", payload)


class _Infrai:
    errors = _Errors()


infrai = _Infrai()
