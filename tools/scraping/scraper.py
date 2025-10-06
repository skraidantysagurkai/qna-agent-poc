import argparse
import json
from collections import Counter
from urllib.parse import urlparse
from typing import Optional, List

import requests
from bs4 import BeautifulSoup
import time
from api.shared.logger import get_logger
from paths import DATA_PATH
import re

LOGGER = get_logger(__name__)


class TextExtractor:
    def __init__(self) -> None:
        self.class_pattern = re.compile(r"page-width|text-start|page-api-block")

    def extract_text_blocks(self, soup: BeautifulSoup) -> str:
        if not soup:
            return ""

        # Find all <p> tags matching class pattern
        paragraphs = soup.find_all("p", class_=self.class_pattern)
        text_chunks = []
        for p in paragraphs:
            # Get text with separator to ensure spaces between elements
            text = p.get_text(separator=" ", strip=True)  # IDE is delulu
            if text:
                text_chunks.append(text)

        return "\n".join(text_chunks)


class Scraper:
    def __init__(self, delay: float = 1.0, batch_size: int = 100) -> None:
        self.delay = delay
        self.batch_size = batch_size
        self.headers = {"User-Agent": "QnA-Bot/0.1"}
        self.text_extractor = TextExtractor()

    def fetch_sitemap_urls(self, sitemap_url: str) -> List[str]:
        LOGGER.info(f"Fetching sitemap: {sitemap_url}")
        resp = requests.get(sitemap_url, timeout=10)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "xml")
        all_urls = [loc.text.strip() for loc in soup.find_all("loc")]
        return all_urls

    def get_url_category(self, url: str) -> Optional[str]:
        path = urlparse(url).path
        parts = [p for p in path.split("/") if p]
        return parts[0] if parts else None

    def scrape_page(self, url: str) -> BeautifulSoup:
        resp = requests.get(url, headers=self.headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        return soup

    def scrape_pages(self, urls: List[str], output_path) -> None:
        results = []
        first_save = True
        total_batches = (len(urls) + self.batch_size - 1) // self.batch_size
        current_batch = 1

        LOGGER.info(f"Starting scraping of {len(urls)} pages in batches of {self.batch_size}")
        for i, url in enumerate(urls):
            try:
                soup = self.scrape_page(url)
                text = self.text_extractor.extract_text_blocks(soup).strip()
                if text:
                    results.append({"url": url, "content": text})
            except Exception as e:
                LOGGER.info(f"Failed to fetch {url}: {e}")
                continue

            time.sleep(self.delay)

            # Save batch when reaching batch_size or at the end
            if len(results) >= self.batch_size or i == len(urls) - 1:
                LOGGER.info(f"Processing batch {current_batch} of {total_batches}")
                self._save_batch(results, output_path, first_save)
                first_save = False
                results = []  # Clear batch
                current_batch += 1

        LOGGER.info("Scraping completed.")

    def _save_batch(self, batch_data: List[dict], output_path, is_first_batch: bool) -> None:
        """Save a batch of scraped data to file."""
        if not batch_data:
            return

        if is_first_batch:
            # First batch: overwrite file
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, ensure_ascii=False, indent=2)
            LOGGER.info(f"Saved first batch of {len(batch_data)} items to {output_path}")
        else:
            # Subsequent batches: append to existing file
            # Read existing data, append new batch, and write back
            try:
                with open(output_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                existing_data = []

            existing_data.extend(batch_data)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            LOGGER.info(f"Appended batch of {len(batch_data)} items to {output_path}")

    def run(self, site_map_url: str, num_sections: int, output_file_name: str) -> None:
        output_path = DATA_PATH / output_file_name

        urls = self.fetch_sitemap_urls(site_map_url)

        url_category_pairs = [(u, self.get_url_category(u)) for u in urls]
        url_category_pairs = [(u, cat) for u, cat in url_category_pairs if cat]

        categories = [cat for _, cat in url_category_pairs]
        counter = Counter(categories)
        top_n = [i[0] for i in counter.most_common(num_sections)]

        filtered_urls = [u for u, cat in url_category_pairs if cat in top_n]

        LOGGER.info(f"Number of urls: {len(filtered_urls)}, top {num_sections} url sections: {top_n}")

        self.scrape_pages(filtered_urls, output_path)

        LOGGER.info(f"All data saved to {output_path}")


def main(site_map_url: str, num_sections: int, output_file_name: str, batch_size: int) -> None:
    scraper = Scraper(delay=0.1, batch_size=batch_size)
    scraper.run(site_map_url, num_sections, output_file_name)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read robot.txt from a website.")
    parser.add_argument(
        "-s",
        "--site_map_url",
        type=str,
        required=True,
        help="Site Map Url",
    )
    parser.add_argument(
        "-n",
        "--num_sections",
        type=int,
        default=2,
        help="Number of sections to scrape",
    )
    parser.add_argument(
        "-o",
        "--output_file_name",
        type=str,
        default="raw_data.json",
        help="Output JSON file name, data will be stored in data folder",
    )
    parser.add_argument(
        "-b",
        "--batch_size",
        type=int,
        default=100,
        help="Size of batch to save data incrementally (not to lose data on crash)",
    )

    return parser


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()

    main(args.site_map_url, args.num_sections, args.output_file_name, args.batch_size)
