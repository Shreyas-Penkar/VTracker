#
#  Code by @xvonfers
#  Refer - https://streypaws.github.io/posts/VTracker/#credits
#
#  Code is modified to turn it into a module for detection of V8/Chromium Commits using Bug ID (to fill up the ones missed in Chrome Release Git Log)
#

import json
import requests
import re

FEED_URL = "https://chromereleases.googleblog.com/feeds/posts/default/-/Stable%20updates"
GITHUB_API = "https://api.github.com/search/commits"
GITHUB_HEADERS = {"Accept": "application/vnd.github.cloak-preview"}
GITHUB_REPOS = ["v8/v8", "chromium/chromium"]
GERRIT_BASE = "https://chromium-review.googlesource.com/changes/"
ISSUES_URL = "https://issues.chromium.org/issues/"

def find_github_commits(bug_id, repo):
    params = {"q": f"repo:{repo} {bug_id}", "sort": "indexed", "order": "desc"}
    r = requests.get(GITHUB_API, headers=GITHUB_HEADERS, params=params, timeout=10)
    if r.status_code != 200:
        return []
    return [item["html_url"] for item in r.json().get("items", [])]

def find_gerrit_changes(bug_id, project):
    q = f"message:{bug_id} project:{project} status:merged"
    r = requests.get(GERRIT_BASE, params={"q": q, "o": "CURRENT_REVISION"}, timeout=10)
    payload = r.text.lstrip(")]}'\n")
    try:
        changes = json.loads(payload)
    except json.JSONDecodeError:
        return []
    return [
        f"https://chromium.googlesource.com/{ch['project']}/+/{ch['current_revision']}"
        for ch in changes
    ]

def extract_issue_title(html, bug_id):
    pattern = r'b\.IssueFetchResponse",\[.*?\[null,' + bug_id + r',\[.*?,.*?,.*?,.*?,.*?,"(.*?)"'
    match = re.search(pattern, html, re.DOTALL)
    if match:
        return match.group(1)
    return None

def check_chromium_issue(bug_id):
    url = f"{ISSUES_URL}{bug_id}"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        if "b.IssueFetchResponse" in r.text:
            title = extract_issue_title(r.text, bug_id)
            if title:
                return f"Issue is accessible: {title}"
            else:
                return "Issue is accessible, but title not found"
        else:
            return "Access to this issue is restricted"
    else:
        return "Failed to retrieve issue information"

def extract_sha_from_github_url(url):
    return url.rstrip("/").split("/")[-1]

def bugid_to_commit(bug_id):
    all_github = []

    # Step 1: Collect GitHub commit URLs
    for repo in GITHUB_REPOS:
        commits = find_github_commits(bug_id, repo)
        if commits:
            all_github += commits

    # Step 2: Match those SHAs with Gerrit commit URLs
    if all_github:
        allowed_shas = {extract_sha_from_github_url(u) for u in all_github}
        filtered = []

        for proj in ("v8/v8", "chromium/src"):
            urls = find_gerrit_changes(bug_id, proj)
            filtered += [u for u in urls if u.split("/")[-1] in allowed_shas]

        # Step 3: Add matching Gerrit URLs to all_github
        all_github += sorted(set(filtered))

    return all_github



