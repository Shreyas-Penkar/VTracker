import re
import requests
import threading
from termcolor import colored

from utils.colors import *
from utils.arg_parser import *
from utils.formatter import print_vulnerabilities
from utils.spinner import loading_spinner

from parsers.git_parser import *
from parsers.release_scraper import text_from_html
from parsers.vulnerability_extractor import extract_vulnerabilities
from parsers.bugid_to_commit import bugid_to_commit, check_chromium_issue

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
            stop_event = threading.Event()
            msg = colored("Please Wait...", 'green')
            spinner_thread = threading.Thread(target=loading_spinner, args=(msg, stop_event))
            spinner_thread.start()

            links= fetch_and_extract_v8_logs(git_log_link[0])
            bug_ids_dict = extract_bug_id_commit_map_from_gitlog_url(git_log_link[0])
            BUG_ID = BUG_ID | bug_ids_dict

            if links != []:
                for link in links:
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

        # Some Bug IDs will show "None" since they might not be present in the Chrome Release Git Log. Hence we need to search for them explicitly.
        for v in VULNS:
            if v["git_link"] == "None":
                v["git_link"] = bugid_to_commit(v["bug_id"])
            
            v["chromium_issue"] = check_chromium_issue(v["bug_id"])

        print()
        print_vulnerabilities(VULNS)
        stop_event.set()
        spinner_thread.join()


if __name__ == "__main__":
    main()
