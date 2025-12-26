import requests
import argparse
import json
import os
import re
import random
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter, deque

# =====================
# USER AGENT ROTATOR (REAL WINDOWS)
# =====================
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Edg/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
    "Gecko/20100101 Firefox/121.0"
]

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

OUTPUT_FILE = "crawl_result.jsonl"

# =====================
# ARGUMENT PARSER
# =====================
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-u", "--url", required=True, help="Start URL")
    p.add_argument("--depth", type=int, default=2, help="Max crawl depth (BFS)")
    return p.parse_args()

# =====================
# KEYWORD DENSITY
# =====================
def keyword_density(text):
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    total = len(words)
    freq = Counter(words)
    top = freq.most_common(10)

    return {
        "total_words": total,
        "top_keywords": [
            {
                "keyword": k,
                "count": c,
                "density": round((c / total) * 100, 2)
            }
            for k, c in top if total > 0
        ]
    }

# =====================
# MAIN CRAWLER
# =====================
def crawl(start_url, max_depth):
    parsed_root = urlparse(start_url)
    base_domain = parsed_root.netloc

    visited = set()        # discovered URLs
    scraped = set()        # already saved URLs
    content_hashes = {}    # hash -> canonical url
    queue = deque([(start_url, 0)])  # BFS (url, depth)

    scraped_count = 0
    session = requests.Session()

    # ===== Resume-safe load =====
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    scraped.add(data["url"])
                    if "content_hash" in data:
                        content_hashes[data["content_hash"]] = data["url"]
                except:
                    pass

    print(f"[+] Starting crawl: {start_url} | Max depth: {max_depth}")

    while queue:
        url, depth = queue.popleft()

        if url in visited or depth > max_depth:
            continue
        visited.add(url)

        headers = HEADERS_BASE.copy()
        headers["User-Agent"] = random.choice(UA_POOL)

        try:
            r = session.get(url, headers=headers, timeout=15)
        except Exception:
            continue

        if "text/html" not in r.headers.get("Content-Type", "").lower():
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # ===== Canonical =====
        canonical = url
        cl = soup.find("link", rel="canonical")
        if cl and cl.get("href"):
            canonical = urljoin(url, cl["href"].strip())

        # ===== Duplicate Detection =====
        content_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        is_duplicate = content_hash in content_hashes
        duplicate_of = content_hashes.get(content_hash)

        if not is_duplicate:
            content_hashes[content_hash] = canonical

        title = soup.title.string.strip() if soup.title else ""
        meta_desc = ""
        md = soup.find("meta", attrs={"name": "description"})
        if md:
            meta_desc = md.get("content", "").strip()

        data = {
            "url": url,
            "canonical": canonical,
            "is_canonical": url == canonical,
            "is_duplicate": is_duplicate,
            "duplicate_of": duplicate_of,
            "status_code": r.status_code,
            "title": title,
            "meta_description": meta_desc,
            "word_count": len(text.split()),
            "keyword_density": keyword_density(text),
            "content_hash": content_hash,
            "depth": depth
        }

        if url not in scraped:
            with open(OUTPUT_FILE, "a") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")

            scraped.add(url)
            scraped_count += 1
            print(f"\r[✓] Scraped URLs: {scraped_count}", end="", flush=True)

        # ===== Discover internal links (BFS) =====
        for a in soup.find_all("a", href=True):
            link = urljoin(url, a["href"])
            p = urlparse(link)

            if p.scheme.startswith("http") and p.netloc == base_domain:
                clean = f"{p.scheme}://{p.netloc}{p.path}"
                if clean not in visited:
                    queue.append((clean, depth + 1))

    print("\n[✓] Crawl finished.")

# =====================
# ENTRY POINT
# =====================
if __name__ == "__main__":
    args = parse_args()
    crawl(args.url, args.depth)
