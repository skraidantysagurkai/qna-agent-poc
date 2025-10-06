import requests
from urllib.parse import urlparse
import argparse


def print_robots_txt(base_url: str):
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    try:
        resp = requests.get(robots_url, timeout=10)
        if resp.status_code == 200:
            print(f"\n===== robots.txt from {robots_url} =====\n")
            print(resp.text)
        else:
            print(f"robots.txt not found (status {resp.status_code}) at {robots_url}")
    except Exception as e:
        print(f"Error fetching robots.txt: {e}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Read robot.txt from a website.")
    parser.add_argument(
        "-b",
        "--base_url",
        help="Base URL",
    )
    return parser


if __name__ == "__main__":
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args()

    print_robots_txt(args.base_url)
