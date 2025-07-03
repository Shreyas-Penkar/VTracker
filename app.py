import re
import requests

from utils.colors import *
from utils.arg_parser import *
from utils.formatter import print_vulnerabilities

from parsers.git_parser import *
from parsers.release_scraper import text_from_html
from parsers.vulnerability_extractor import extract_vulnerabilities

VULNS = []
BUG_ID = {}

def main():
    global VULNS, BUG_ID
    year, month = parse_args()
    release_url = construct_release_url(year, month)
    release_pattern = construct_chrome_release_regex(year, month)

    is_internet_working()
    green(f"✅ Fetching URL: {release_url}")
    res = requests.get(release_url)
    if res.status_code != 200:
        red(f"❌ Failed to fetch archive page: {res.status_code}")
        return

    post_links = sorted(set(re.findall(release_pattern, res.text)))
    if not post_links:
        red("❗ No matching chrome release URLs found.")
        return

    green(f"✅ Found Advisories on {len(post_links)} Dates.\n")

    for url in post_links:
        yellow(f"\n=== Fetching and processing: {url} ===\n")
        response = requests.get(url)
        if response.status_code != 200:
            red(f"Failed to fetch {url}, status code: {response.status_code}")
            continue

        page_text = text_from_html(response.text)
        VULNS = extract_vulnerabilities(page_text)

        if not VULNS:
            red("❌ No vulnerability information found.")
            continue

        git_log_link = extract_git_log_links(response.text)
        if git_log_link:
            magenta("🔗 Chromium Git Log Link: " + git_log_link[0])
            print()
            links = fetch_and_extract_v8_logs(git_log_link[0])
            for link in links:
                print(f"  {link}")
                commit_links = extract_commit_links(link)
                for commit_link in commit_links:
                    bug_ids = extract_bug_ids_from_commit_url(commit_link)
                    if bug_ids is not None:
                        for bug_id in bug_ids:
                            BUG_ID[bug_id] = commit_link
        else:
            red("❌ No Git Log link found.")

        for v in VULNS:
            if v["bug_id"] in BUG_ID:
                v["git_link"] = BUG_ID[v["bug_id"]]

        print_vulnerabilities(VULNS)


if __name__ == "__main__":
    main()
