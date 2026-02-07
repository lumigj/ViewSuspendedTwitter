import html as html_module
import json
import re
import urllib.request

# 抓取原本的，没啥用，因为这个要重新联网
def fetch_snapshot_content(timestamp: str, original_url: str) -> str:
    archive_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
    with urllib.request.urlopen(archive_url) as resp:
        return resp.read().decode("utf-8", errors="replace")

# 抓取iframe里的

def fetch_snapshot_content_iframe(timestamp: str, original_url: str) -> str:
    archive_url = f"https://web.archive.org/web/{timestamp}if_/{original_url}"
    with urllib.request.urlopen(archive_url) as resp:
        return resp.read().decode("utf-8", errors="replace")


#留下iframe html里面真正有用的信息
def build_simplified_tweet_html(iframe_html: str) -> str:
    match = re.search(r"<pre>(.*?)</pre>", iframe_html, re.DOTALL)
    if not match:
        return iframe_html

    try:
        raw_json = html_module.unescape(match.group(1).strip())
        payload = json.loads(raw_json)
    except json.JSONDecodeError:
        return iframe_html

    data = payload.get("data", {})
    includes = payload.get("includes", {})
    users = includes.get("users", [])
    author_id = data.get("author_id")
    author = next((u for u in users if u.get("id") == author_id), {})

    name = html_module.escape(author.get("name", ""))
    username = html_module.escape(author.get("username", ""))
    text = html_module.escape(data.get("text", ""))
    created_at = html_module.escape(data.get("created_at", ""))

    return f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>Tweet Snapshot</title>
    <style>
      body {{
        margin: 0;
        padding: 24px;
        font-family: Helvetica, Arial, sans-serif;
        background: #f7f7f7;
      }}
      .tweet {{
        max-width: 680px;
        margin: 0 auto;
        background: #fff;
        border: 1px solid #d9d9d9;
        border-radius: 12px;
        padding: 16px 20px;
      }}
      .author {{
        font-weight: 700;
        margin-bottom: 4px;
      }}
      .username {{
        color: #657786;
        margin-bottom: 12px;
      }}
      .content {{
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
      }}
      .date {{
        margin-top: 12px;
        color: #657786;
        font-size: 0.85rem;
      }}
    </style>
  </head>
  <body>
    <article class="tweet">
      <div class="author">{name}</div>
      <div class="username">@{username}</div>
      <div class="content">{text}</div>
      <div class="date">{created_at}</div>
    </article>
  </body>
</html>
"""


__all__ = [
    "fetch_snapshot_content",
    "fetch_snapshot_content_iframe",
    "build_simplified_tweet_html",
]


if __name__ == "__main__":
    example_timestamp = "20241009081148"
    example_url = "https://twitter.com/nekomakiQAQ/status/1843927329254584430"
    iframe_html = fetch_snapshot_content_iframe(example_timestamp, example_url)
    print(build_simplified_tweet_html(iframe_html))
