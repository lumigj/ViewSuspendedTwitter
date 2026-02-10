import html as html_module
import json
import re
import urllib.request

USER_AGENT = "ViewSuspendedTwitter/1.0 (+https://web.archive.org/)"


def _open_url(url: str, timeout_seconds: int | None = None) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_snapshot_content(timestamp: str, original_url: str, timeout_seconds: int | None = None) -> str:
    archive_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
    return _open_url(archive_url, timeout_seconds)

# 抓取iframe里的

def fetch_snapshot_content_iframe(timestamp: str, original_url: str, timeout_seconds: int | None = None) -> str:
    archive_url = f"https://web.archive.org/web/{timestamp}if_/{original_url}"
    return _open_url(archive_url, timeout_seconds)


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
    bio = html_module.escape(author.get("description", ""))
    profile_image_url = html_module.escape(author.get("profile_image_url", ""))
    author_created_at = html_module.escape(author.get("created_at", ""))
    author_metrics = author.get("public_metrics", {}) or {}
    author_followers = author_metrics.get("followers_count", "")
    author_following = author_metrics.get("following_count", "")
    author_tweets = author_metrics.get("tweet_count", "")
    author_likes = author_metrics.get("like_count", "")
    author_listed = author_metrics.get("listed_count", "")
    author_media = author_metrics.get("media_count", "")

    text = html_module.escape(data.get("text", ""))
    created_at = html_module.escape(data.get("created_at", ""))
    conversation_id = html_module.escape(data.get("conversation_id", ""))
    referenced_tweets = data.get("referenced_tweets", []) or []
    referenced_summary = ", ".join(
        f"{t.get('type', '')}:{t.get('id', '')}" for t in referenced_tweets
    )
    referenced_summary = html_module.escape(referenced_summary)

    tweet_metrics = data.get("public_metrics", {}) or {}
    reply_count = tweet_metrics.get("reply_count", "")
    retweet_count = tweet_metrics.get("retweet_count", "")
    like_count = tweet_metrics.get("like_count", "")
    quote_count = tweet_metrics.get("quote_count", "")
    bookmark_count = tweet_metrics.get("bookmark_count", "")
    impression_count = tweet_metrics.get("impression_count", "")

    mentions = data.get("entities", {}).get("mentions", []) or []
    mention_list = ", ".join(f"@{m.get('username', '')}" for m in mentions)
    mention_list = html_module.escape(mention_list)

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
        margin-bottom: 8px;
      }}
      .bio {{
        color: #374151;
        margin-bottom: 12px;
      }}
      .author-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 12px;
        color: #4b5563;
        font-size: 0.9rem;
      }}
      .content {{
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
      }}
      .metrics {{
        margin-top: 12px;
        color: #4b5563;
        font-size: 0.9rem;
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
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
      <div class="bio">{bio}</div>
      <div class="author-meta">
        <span>Profile image: {profile_image_url}</span>
        <span>Joined: {author_created_at}</span>
        <span>Followers: {author_followers}</span>
        <span>Following: {author_following}</span>
        <span>Tweets: {author_tweets}</span>
        <span>Likes: {author_likes}</span>
        <span>Listed: {author_listed}</span>
        <span>Media: {author_media}</span>
      </div>
      <div class="content">{text}</div>
      <div class="metrics">
        <span>Replies: {reply_count}</span>
        <span>Retweets: {retweet_count}</span>
        <span>Likes: {like_count}</span>
        <span>Quotes: {quote_count}</span>
        <span>Bookmarks: {bookmark_count}</span>
        <span>Impressions: {impression_count}</span>
      </div>
      <div class="date">Created at: {created_at}</div>
      <div class="date">Conversation: {conversation_id}</div>
      <div class="date">Referenced tweets: {referenced_summary}</div>
      <div class="date">Mentions: {mention_list}</div>
    </article>
  </body>
</html>
"""

def extract_iframe_data(iframe_html: str) -> str:
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
    bio = html_module.escape(author.get("description", ""))
    profile_image_url = html_module.escape(author.get("profile_image_url", ""))
    author_created_at = html_module.escape(author.get("created_at", ""))
    author_metrics = author.get("public_metrics", {}) or {}
    author_followers = author_metrics.get("followers_count", "")
    author_following = author_metrics.get("following_count", "")
    author_tweets = author_metrics.get("tweet_count", "")
    author_likes = author_metrics.get("like_count", "")
    author_listed = author_metrics.get("listed_count", "")
    author_media = author_metrics.get("media_count", "")

    text = html_module.escape(data.get("text", ""))
    created_at = html_module.escape(data.get("created_at", ""))
    conversation_id = html_module.escape(data.get("conversation_id", ""))
    referenced_tweets = data.get("referenced_tweets", []) or []
    referenced_summary = ", ".join(
        f"{t.get('type', '')}:{t.get('id', '')}" for t in referenced_tweets
    )
    referenced_summary = html_module.escape(referenced_summary)

    tweet_metrics = data.get("public_metrics", {}) or {}
    reply_count = tweet_metrics.get("reply_count", "")
    retweet_count = tweet_metrics.get("retweet_count", "")
    like_count = tweet_metrics.get("like_count", "")
    quote_count = tweet_metrics.get("quote_count", "")
    bookmark_count = tweet_metrics.get("bookmark_count", "")
    impression_count = tweet_metrics.get("impression_count", "")

    mentions = data.get("entities", {}).get("mentions", []) or []
    mention_list = ", ".join(f"@{m.get('username', '')}" for m in mentions)
    mention_list = html_module.escape(mention_list)

    return {
        "name": name,
        "username": username,
        "bio": bio,
        "profile_image_url": profile_image_url,
        "author_created_at": author_created_at,
        "author_followers": author_followers,
        "author_following": author_following,
        "author_tweets": author_tweets,
        "author_likes": author_likes,
        "author_listed": author_listed,
        "author_media": author_media,
        
        "text": text,
        "created_at": created_at,
        "conversation_id": conversation_id,

        "reply_count": reply_count,
        "retweet_count": retweet_count,
        "like_count": like_count,
        "quote_count": quote_count,
        "bookmark_count": bookmark_count,
        "impression_count": impression_count,
        }


__all__ = [
    "fetch_snapshot_content",
    "fetch_snapshot_content_iframe",
    "build_simplified_tweet_html",
    "extract_iframe_data",
]


#一个snapshot的例子
if __name__ == "__main__":
    example_timestamp = "20251012170444"
    example_url = "https://x.com/NekoMakiQAQ/status/1977420179576700944"
    iframe_html = fetch_snapshot_content_iframe(example_timestamp, example_url)
    print(build_simplified_tweet_html(iframe_html))
