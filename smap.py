import requests
import argparse
import os
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

CHUNK_SIZE = 500
OUT_DIR = "sitemap_output"
os.makedirs(OUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
}

def fetch_xml(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def parse_sitemap(xml_text):
    root = ET.fromstring(xml_text)
    ns = {"ns": root.tag.split("}")[0].strip("{")}

    # sitemap index
    if root.tag.endswith("sitemapindex"):
        return [loc.text for loc in root.findall("ns:sitemap/ns:loc", ns)]

    # urlset
    elif root.tag.endswith("urlset"):
        return [loc.text for loc in root.findall("ns:url/ns:loc", ns)]

    else:
        return []

def save_chunks(urls):
    file_index = 1
    buffer = []

    for i, url in enumerate(urls, 1):
        buffer.append({"url": url})

        if len(buffer) == CHUNK_SIZE:
            path = f"{OUT_DIR}/urls_{file_index}.jsonl"
            with open(path, "a", encoding="utf-8") as f:
                for row in buffer:
                    f.write(json.dumps(row) + "\n")
            print(f"[✓] Saved {file_index * CHUNK_SIZE} URLs", end="\r", flush=True)
            buffer.clear()
            file_index += 1

    # sisa
    if buffer:
        path = f"{OUT_DIR}/urls_{file_index}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            for row in buffer:
                f.write(json.dumps(row) + "\n")
        print(f"[✓] Saved total {((file_index-1)*CHUNK_SIZE)+len(buffer)} URLs")

def main(sitemap_url):
    print("[*] Fetching sitemap index...")
    xml = fetch_xml(sitemap_url)
    items = parse_sitemap(xml)

    all_urls = set()

    # Jika sitemap index
    if items and items[0].endswith(".xml"):
        for sm in items:
            print(f"[*] Parsing child sitemap: {sm}")
            xml_child = fetch_xml(sm)
            urls = parse_sitemap(xml_child)
            all_urls.update(urls)
    else:
        all_urls.update(items)

    print(f"[*] Total unique URLs: {len(all_urls)}")
    save_chunks(sorted(all_urls))
    print("\n[✓] DONE")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", required=True, help="Sitemap index URL")
    args = parser.parse_args()

    main(args.url) # py smap.py -u https://site.com/sitemap_index.xml
