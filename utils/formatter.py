from termcolor import colored
from utils.colors import magenta

def print_vulnerabilities(VULNS):
    print()
    for i, v in enumerate(VULNS, 1):
        magenta(f"Vulnerability #{i}:\n")

        def line(label, value):
            print(f"{colored(label + ':', 'cyan'):<18} {colored(str(value), 'white')}")

        line("CVE ID", v.get('cve', 'Unknown'))
        line("Bug ID", v['bug_id'])
        line("Severity", v['severity'])
        line("Bounty", v['bounty'])
        line("Description", v['description'])
        line("Reported by", v['reported_by'])

        # Format git_link as a clean list
        git_links = v.get('git_link', [])
        if isinstance(git_links, str):
            git_links = [git_links]  # wrap as list

        if git_links:
            print(f"{colored('Commit Links:', 'cyan'):<18} {colored(git_links[0], 'white')}")
            for link in git_links[1:]:
                print(f"{'':<13} {colored(link, 'white')}")
        else:
            line("Commit Links", "None")

        line("Chromium Issue", v['chromium_issue'])

        print("\n" + "-" * 60 + "\n")

