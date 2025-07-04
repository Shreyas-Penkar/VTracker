import argparse, sys
from datetime import datetime
from utils.colors import *

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()

    current_year = datetime.now().year
    if not (2009 <= args.year <= current_year):
        red("❌ Year must be between 2009 and the current year.")
        sys.exit(1)
    if not (1 <= args.month <= 12):
        red("❌ Month must be between 1 and 12.")
        sys.exit(1)

    return args.year, args.month

def construct_release_url(year, month):
    padded_month = f"{month:02d}"
    return f"https://chromereleases.googleblog.com/{year}/{padded_month}/"

def construct_chrome_release_regex(year, month):
    padded_month = f"{month:02d}"
    return (
        rf"https://chromereleases\.googleblog\.com/{year}/{padded_month}/"
        r"stable-channel-update-for-desktop_\d{1,2}\.html"
    )
