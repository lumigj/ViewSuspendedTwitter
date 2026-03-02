import json
import os
import sqlite3
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


def fetch_cdx_rows(in_username: str) -> list[list[str]]:
    query = urllib.parse.urlencode(build_params(in_username))
    url = f"{CDX_ENDPOINT}?{query}"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    return data[1:] if data else []


def write_cdx_rows(in_username: str, rows: list[list[str]]) -> str:
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{in_username}.db")
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
