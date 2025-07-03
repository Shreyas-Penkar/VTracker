import re, sys
import requests, socket
from bs4 import BeautifulSoup
from utils.colors import red

def is_internet_working(host="www.google.com", port=80, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection((host, port))
    except OSError:
        red("❌ No internet connection.")
        sys.exit(1)

def extract_git_log_links(html_text):
    pattern = re.compile(r"https://chromium\.googlesource\.com/chromium/src/\+log/[^\"']+")
    return sorted(set(re.findall(pattern, html_text)))

def extract_bug_ids_from_commit_url(commit_url):
    try:
        resp = requests.get(commit_url)
        resp.raise_for_status()
    except requests.RequestException as e:
        red(f"❌ Failed to fetch: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    pre = soup.find("pre", class_="u-pre u-monospace MetadataMessage")
    if not pre:
        return None

    text = pre.get_text()
    bug_lines = re.findall(r'(?:Bug|Fixed):\s*([0-9,\s]+)', text)

    bug_ids = set()
    for line in bug_lines:
        ids = re.split(r'[,\s]+', line)
        bug_ids.update(filter(None, ids))

    return sorted(bug_ids) if bug_ids else None

def extract_commit_links(v8_log_url):
    res = requests.get(v8_log_url)
    if res.status_code != 200:
        red(f"❌ Failed to fetch: HTTP {res.status_code}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    pattern = re.compile(r"^/v8/v8\.git/\+/[a-f0-9]{40}$")

    links = [
        f"https://chromium.googlesource.com{a['href']}"
        for a in soup.find_all("a", href=True)
        if pattern.match(a["href"])
    ]
    return sorted(set(links))

def fetch_and_extract_v8_logs(git_log_url):
    res = requests.get(git_log_url)
    if res.status_code != 200:
        red(f"❌ Failed to fetch: HTTP {res.status_code}")
        return []

    html = res.text
    pattern = re.compile(r"https://chromium\.googlesource\.com/v8/v8\.git/\+log/[^\"'<>\s]+")
    return sorted(set(re.findall(pattern, html)))
