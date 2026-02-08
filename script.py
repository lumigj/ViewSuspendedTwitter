import json
import urllib.parse
import urllib.request

CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"


def build_params(username: str) -> dict[str, str]:
    return {
        "url": f"twitter.com/{username}/status/*",
        "output": "json",
        "fl": "timestamp,original",
        "collapse": "urlkey",
        "sort": "desc",
        # "limit": "10",
    }


def fetch_cdx_rows(username: str) -> list[list[str]]:
    query = urllib.parse.urlencode(build_params(username))
    url = f"{CDX_ENDPOINT}?{query}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return data[1:] if data else []


__all__ = ["fetch_cdx_rows", "build_params"]
