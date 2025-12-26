scrweb — Lightweight SEO Web Crawler (Windows, Linux, Mac, Termux)

scrweb adalah SEO-focused web crawler berbasis Python yang dirancang sebagai alternatif ringan Screaming Frog untuk audit internal link, konten, dan duplikasi, tanpa batas URL dan aman dijalankan di Termux.

Tool ini tidak melakukan JavaScript rendering dan berfokus pada HTML crawl murni, sesuai kebutuhan audit SEO teknikal dan konten.


---

✨ Fitur Utama

🔹 Crawling Core

Crawl dari 1 URL input

HTML only (berdasarkan Content-Type)

Unlimited URL (tanpa limit artificial)

Internal link only

Anti duplikat (URL & konten)

Autosave (append) → aman jika crash

Resume-safe (tidak re-save URL lama)

1-line live counter (tidak spam terminal)



---

🔹 Crawl Depth Control (BFS)

Breadth-First Search (SEO-friendly)

Kontrol kedalaman crawl (--depth)

Mencegah infinite crawl (pagination, tag, archive)


Contoh:

depth 0 → URL awal
depth 1 → link langsung
depth 2 → link dari link


---

🔹 Canonical & Duplicate Content Detection

Deteksi <link rel="canonical">

Tandai:

self-canonical

non-canonical

canonical conflict


Duplicate content detection berbasis content hash

Mapping URL → canonical → duplicate_of



---

🔹 SEO Metrics (Sesuai Scope)

HTTP Status Code

Title tag

Meta description

Word count

Keyword density (Top 10 + %)


> ⚠️ Heading (H1–H6) sengaja tidak dianalisis sesuai desain awal.




---

🔹 Stealth & Compatibility

User-Agent rotator (Real Windows)
Chrome / Edge / Firefox

Header browser-like

Tanpa lxml → 100% kompatibel dengan Termux

Tidak butuh dependency berat



---

📦 Output

File

crawl_result.jsonl

Format

JSON Lines

1 baris = 1 URL

Aman untuk dataset besar

Bisa diproses ulang (Python, jq, pandas)


Contoh Output

{
  "url": "https://site.com/page",
  "canonical": "https://site.com/page",
  "is_canonical": true,
  "is_duplicate": false,
  "duplicate_of": null,
  "status_code": 200,
  "title": "Contoh Judul",
  "meta_description": "Deskripsi halaman",
  "word_count": 842,
  "keyword_density": {
    "total_words": 842,
    "top_keywords": [
      {"keyword": "seo", "count": 21, "density": 2.49}
    ]
  },
  "content_hash": "e4d909c290d0fb1ca068ffaddf22cbd0",
  "depth": 1
}


---

▶ Cara Install

1️⃣ Dependency

pip install requests beautifulsoup4

(Tidak perlu lxml)


---

2️⃣ Run

py scrweb.py -u https://site.com/articles --depth 2

Parameter

Flag	Keterangan

-u / --url	URL awal (wajib)
--depth	Maksimum crawl depth (default: 2)



---

🧠 Cara Kerja Singkat

1. Mulai dari URL input


2. BFS crawl sampai max_depth


3. Filter HTML only


4. Extract konten & metadata


5. Deteksi canonical & duplicate


6. Autosave hasil per URL


7. Update counter real-time




---

⚠️ Batasan (By Design)

Tool ini tidak:

Render JavaScript

Crawl external domain

Respect robots.txt (belum)

Parse sitemap.xml (belum)

Mengukur PageSpeed / CWV


Fitur di atas sengaja tidak diaktifkan demi kesederhanaan dan kontrol penuh.


---

🚀 Roadmap (Opsional)

Robots.txt & sitemap enforcement

Crawl performance metrics (URL/min, ETA)

CSV & SEO summary report

Canonical conflict visualization



---

⚖️ Disclaimer

> Seluruh isi dan penggunaan tool ini bersifat edukatif dan analitis, tidak ditujukan untuk aktivitas ilegal atau pelanggaran kebijakan website. Gunakan hanya pada domain yang Anda miliki atau memiliki izin eksplisit untuk dianalisis.




---

👤 Target Pengguna

SEO technical analyst

Content auditor

Website owner

Research & internal crawl analysis
