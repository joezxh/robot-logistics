"""
MuJoCo manual crawler (robust edition).

- Recursively fetch the stable docs site, convert each page to Markdown,
  download images locally, rewrite internal links (.html -> .md).
- Only downloads pages that are MISSING locally (skips already-crawled files).
- Every URL logs start/finish/skip/fail with elapsed time.
- A per-URL hard timeout (watchdog thread) detects "stuck" fetches and
  reports the reason instead of hanging forever.

Output: docs/mujoco-manual/
  <page>.md      one Markdown file per page, mirroring site tree
  images/<name>  downloaded images

Run:  python crawl.py
"""
import os
import sys
import time
import html2text
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from threading import Thread

BASE = "https://mujoco.readthedocs.io/en/stable/"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(OUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (compatible; mujoco-manual-crawler/1.0)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

HTTP_TIMEOUT = 30          # requests timeout (connect+read)
HARD_TIMEOUT = 60         # watchdog: abort a single URL after this many seconds
MAX_RETRIES = 2

visited = set()           # urls whose processing was attempted
md_paths = {}             # url -> relative markdown path
image_map = {}            # url -> local relative path


# --------------------------------------------------------------------------- #
# logging helpers
# --------------------------------------------------------------------------- #
def log(msg):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def local_md_path(url):
    """Absolute path of the Markdown file that would store `url`."""
    md_rel = url_to_mdpath(url)
    return os.path.join(OUT_DIR, *md_rel.split("/")) + ".md"


def exists_locally(url):
    return os.path.exists(local_md_path(url))


# --------------------------------------------------------------------------- #
# fetching with hard timeout (watchdog thread)
# --------------------------------------------------------------------------- #
def _fetch_with_timeout(url):
    """Return (html_text_or_None, reason_or_None).

    reason is set when the fetch is aborted by the watchdog.
    """
    result = {"html": None, "err": None, "done": False}

    def worker():
        try:
            last = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    log(f"  GET attempt {attempt}/{MAX_RETRIES} -> {url}")
                    r = SESSION.get(url, timeout=HTTP_TIMEOUT)
                    r.encoding = "utf-8"
                    if r.status_code == 200:
                        result["html"] = r.text
                        result["done"] = True
                        return
                    last = f"HTTP {r.status_code}"
                    log(f"  unexpected status {r.status_code} for {url}")
                except requests.exceptions.Timeout:
                    last = f"timeout (> {HTTP_TIMEOUT}s on attempt {attempt})"
                    log(f"  TIMEOUT {url} (attempt {attempt})")
                except requests.exceptions.ConnectionError as e:
                    last = f"connection error: {e}"
                    log(f"  CONN-ERR {url}: {e}")
                except Exception as e:  # noqa: BLE001
                    last = f"exception: {type(e).__name__}: {e}"
                    log(f"  EXC {url}: {e}")
                time.sleep(2)
            result["err"] = last or "unknown failure"
        except Exception as e:  # noqa: BLE001
            result["err"] = f"worker crashed: {e}"

    t = Thread(target=worker, daemon=True)
    t.start()
    t.join(HARD_TIMEOUT)
    if t.is_alive():
        # watchdog tripped -> treat as stuck
        return None, (
            f"WATCHDOG: fetch stuck > {HARD_TIMEOUT}s "
            f"(no response from server, DNS hang, or infinite redirect)"
        )
    if result["done"]:
        return result["html"], None
    return None, result["err"]


# --------------------------------------------------------------------------- #
# path / parsing helpers
# --------------------------------------------------------------------------- #
def url_to_mdpath(url):
    path = urlparse(url).path
    idx = path.find("/en/stable/")
    if idx >= 0:
        path = path[idx + len("/en/stable/"):]
    if path.endswith("/"):
        path += "index.html"
    if not path.endswith(".html"):
        if not path:
            path = "index.html"
        else:
            path += "/index.html"
    return path[:-5]  # drop .html


def download_image(img_url, page_url):
    if img_url in image_map:
        return image_map[img_url]
    abs_url = urljoin(page_url, img_url)
    name = os.path.basename(urlparse(abs_url).path)
    dest_rel = "images/" + name
    dest_abs = os.path.join(IMG_DIR, name)
    if os.path.exists(dest_abs):
        image_map[img_url] = dest_rel
        return dest_rel
    data, reason = _fetch_with_timeout(abs_url)
    if data is None:
        log(f"  IMG FAIL {abs_url} -> {reason}")
        image_map[img_url] = abs_url  # fallback: keep absolute
        return abs_url
    if isinstance(data, str):
        data = data.encode("utf-8")
    with open(dest_abs, "wb") as f:
        f.write(data)
    image_map[img_url] = dest_rel
    return dest_rel


def collect_links(soup, page_url):
    links = set()
    nav = soup.select_one("aside.sidebar-drawer") or soup.select_one(".sidebar-tree")
    if nav:
        for a in nav.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".html") and not href.startswith("http"):
                links.add(urljoin(page_url, href))
    art = soup.select_one("article") or soup.select_one(".content")
    if art:
        for a in art.find_all("a", href=True):
            href = a["href"]
            if href.endswith(".html") and not href.startswith("http"):
                links.add(urljoin(page_url, href))
    return links


def extract_body(soup, page_url):
    art = soup.select_one("article") or soup.select_one(".content")
    if art is None:
        return None
    for sel in ["nav", ".toc-drawer", "aside", "a.headerlink"]:
        for el in art.select(sel):
            el.decompose()
    for img in art.find_all("img"):
        src = img.get("src")
        if not src:
            continue
        img["src"] = download_image(src, page_url)
    for a in art.find_all("a", href=True):
        href = a["href"]
        if href.startswith("http"):
            continue
        base, frag = (href.split("#", 1) + [""])[:2]
        if not base.endswith(".html"):
            continue
        abs_url = urljoin(page_url, base)
        mdrel = url_to_mdpath(abs_url) + ".md"
        a["href"] = (mdrel + "#" + frag) if frag else mdrel
    return str(art)


def html_to_md(html_str, page_url):
    h = html2text.HTML2Text()
    h.baseurl = page_url
    h.body_width = 0
    h.ignore_links = False
    h.ignore_images = False
    h.images_to_alt = False
    h.single_line_break = False
    h.unicode_snob = True
    h.skip_internal_links = False
    return h.handle(html_str)


# --------------------------------------------------------------------------- #
# crawl driver (explicit queue, per-URL timeout)
# --------------------------------------------------------------------------- #
def crawl_missing(start_urls):
    queue = list(start_urls)
    while queue:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        if exists_locally(url):
            log(f"SKIP (already on disk): {url}")
            # still need its links to discover other missing pages,
            # but fetching the full HTML just for links is cheap-ish;
            # we fetch (with timeout) only to harvest links.
            html, reason = _fetch_with_timeout(url)
            if html is None:
                log(f"  LINK-SCAN FAILED for {url}: {reason}")
                continue
            soup = BeautifulSoup(html, "lxml")
            for link in collect_links(soup, url):
                if link not in visited:
                    queue.append(link)
            continue

        log(f"FETCH {url}")
        t0 = time.time()
        html, reason = _fetch_with_timeout(url)
        dt = time.time() - t0
        if html is None:
            log(f"  FAILED after {dt:.1f}s: {url} | reason: {reason}")
            continue
        try:
            soup = BeautifulSoup(html, "lxml")
            body_html = extract_body(soup, url)
            if body_html is None:
                log(f"  NO BODY after {dt:.1f}s: {url}")
                continue
            md = html_to_md(body_html, url)
            out = local_md_path(url)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as f:
                f.write(md)
            md_paths[url] = url_to_mdpath(url)
            log(f"  SAVED {url} -> {out} ({len(md)} chars, {dt:.1f}s)")
        except Exception as e:  # noqa: BLE001
            log(f"  PARSE/WRITE ERROR {url}: {e}")
            continue

        for link in collect_links(soup, url):
            if link not in visited:
                queue.append(link)

    log(f"DONE. visited={len(visited)} saved={len(md_paths)} images={len(image_map)}")


if __name__ == "__main__":
    log("=== MuJoCo manual crawl start ===")
    seeds = [
        urljoin(BASE, "overview.html"),
        urljoin(BASE, "index.html"),
        urljoin(BASE, "models.html"),
        urljoin(BASE, "computation/index.html"),
        urljoin(BASE, "OpenUSD/building.html"),
        urljoin(BASE, "OpenUSD/mjcf_file_format_plugin.html"),
    ]
    try:
        crawl_missing(seeds)
    except KeyboardInterrupt:
        log("INTERRUPTED by user")
    log("=== crawl finished ===")
