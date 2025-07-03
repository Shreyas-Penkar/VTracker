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
        line("Commit Link", v['git_link'])

        print("\n" + "-" * 60 + "\n")
