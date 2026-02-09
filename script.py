import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request

CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
USER_AGENT = "ViewSuspendedTwitter/1.0 (+https://web.archive.org/)"


def build_params(username: str) -> dict[str, str]:
    return {
        "url": f"twitter.com/{username}/status/*",
        "output": "json",
        "fl": "timestamp,original",
        "collapse": "urlkey",
        "sort": "desc",
        # "limit": "10",
    }


def fetch_cdx_rows(username: str, *, retries: int = 4, timeout_seconds: int = 15) -> list[list[str]]:
    query = urllib.parse.urlencode(build_params(username))
    url = f"{CDX_ENDPOINT}?{query}"
    last_exc: Exception | None = None

    for attempt in range(retries):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout_seconds) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
            return data[1:] if data else []
        except Exception as exc:
            last_exc = exc
            # Exponential backoff: 1s, 2s, 4s, 8s...
            time.sleep(2**attempt)

    raise last_exc if last_exc else RuntimeError("Failed to fetch CDX rows")


def write_cdx_rows(username: str, rows: list[list[str]]) -> str:
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{username}.db")
    with sqlite3.connect(output_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                timestamp TEXT NOT NULL,
                original TEXT NOT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                PRIMARY KEY (timestamp, original)
            )
            """
        )
        conn.executemany(
            """
            INSERT OR IGNORE INTO snapshots (timestamp, original)
            VALUES (?, ?)
            """,
            [(row[0], row[1]) for row in rows],
        )
        conn.commit()
    return output_path


__all__ = ["fetch_cdx_rows", "build_params", "write_cdx_rows"]

#run这个会直接存一遍下面username的database
if __name__ == "__main__":
    username = "susiethegamer"
    output = write_cdx_rows(username, fetch_cdx_rows(username))
    print(output)

