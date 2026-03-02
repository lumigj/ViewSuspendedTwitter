import os
import re
import sqlite3
import time

from script import fetch_cdx_rows, write_cdx_rows
from snapshot import build_simplified_tweet_html, fetch_snapshot_content_iframe


def sanitize_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")


def load_pending_rows(db_path: str) -> list[tuple[str, str]]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT timestamp, original
            FROM snapshots
            WHERE status IN (0, 2)
            ORDER BY timestamp DESC
            """
        ).fetchall()
        # WHERE status IN (0, 2)
    return [(row[0], row[1]) for row in rows]


def mark_row(db_path: str, timestamp: str, original: str, status: int, error: str | None) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE snapshots
            SET status = ?,
                error = ?
            WHERE timestamp = ? AND original = ?
            """,
            (status, error, timestamp, original),
        )
        conn.commit()
    print(f"== Marked row: {timestamp} {original} status={status}")

def save_snapshots(rows: list[tuple[str, str]], username: str, db_path: str) -> None:
    total = len(rows)
    print(f"Total pending rows: {total}")
    for timestamp, original in rows:
        print(f"Fetching snapshot: {timestamp} {original}")
        output_dir = f"output/{username}"
        os.makedirs(output_dir, exist_ok=True)
        try:
            iframe_html = fetch_snapshot_content_iframe(timestamp, original, timeout_seconds=10)
            print("== Fetched snapshot, building HTML...")
            simplified_html = build_simplified_tweet_html(iframe_html)
            safe_original = sanitize_filename(original)
            output_name = f"snapshot_{timestamp}_{safe_original}.html"
            output_path = os.path.join(output_dir, output_name)
            print(f"== Writing file: {output_path}")
            with open(output_path, "w", encoding="utf-8") as handle:
                handle.write(simplified_html)
            mark_row(db_path, timestamp, original, 1, None)
            print([timestamp, original, output_path])
        except Exception as exc:
            mark_row(db_path, timestamp, original, 2, str(exc))
            print([timestamp, original, str(exc)])
        time.sleep(1.5)  # 不然一直跳


def main() -> None:
    username = "lumicatroll"
    db_path = os.path.join("output", f"{username}.db")
    if not os.path.exists(db_path):
        db_path = write_cdx_rows(username, fetch_cdx_rows(username))
    rows = load_pending_rows(db_path)
    save_snapshots(rows, username, db_path)


if __name__ == "__main__":
    main()
