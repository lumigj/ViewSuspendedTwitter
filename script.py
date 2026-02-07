import json
import urllib.parse
import urllib.request

CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"


params = {
    "url": "twitter.com/NekoMakiQAQ/status/*",
    "output": "json",
    "fl": "timestamp,original",
    "collapse": "urlkey",
    # "sort": "desc", // 加这个就是从最新日期开始，不加就是最老的
    "limit": "10",
}

query = urllib.parse.urlencode(params)
url = f"{CDX_ENDPOINT}?{query}"

with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode("utf-8", errors="replace"))

rows = data[1:] if data else []
for row in rows:
    print([row[0], row[1]])
