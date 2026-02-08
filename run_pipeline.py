import os
import re

from script import fetch_cdx_rows
from snapshot import build_simplified_tweet_html, fetch_snapshot_content_iframe


def sanitize_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")


def save_snapshots(rows: list[list[str]], username: str) -> None:
    for row in rows:
        timestamp, original = row[0], row[1]
        iframe_html = fetch_snapshot_content_iframe(timestamp, original)
        simplified_html = build_simplified_tweet_html(iframe_html)
        safe_original = sanitize_filename(original)
        output_dir = f"output/{username}"
        os.makedirs(output_dir, exist_ok=True)
        output_name = f"snapshot_{timestamp}_{safe_original}.html"
        output_path = os.path.join(output_dir, output_name)
        with open(output_path, "w", encoding="utf-8") as handle:
            handle.write(simplified_html)
        print([timestamp, original, output_path])


def main() -> None:
    username = "NekoMakiQAQ"
    rows = fetch_cdx_rows(username)
    save_snapshots(rows, username)


if __name__ == "__main__":
    main()
