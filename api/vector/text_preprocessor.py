import json
import re
from typing import List
from urllib.parse import urlparse

from pydantic import BaseModel

from api.shared.logger import get_logger
from api.vector.store import ContextEntry

LOGGER = get_logger(__name__)


class TextEntry(BaseModel):
    url: str
    content: str


class RawDataPreprocessor:
    def __init__(self):
        pass

    @staticmethod
    def read_json_file(file_path: str) -> List[TextEntry]:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    data = [data]
                return [TextEntry(**item) for item in data if "url" in item and "content" in item]
        except Exception as e:
            LOGGER.error(f"Error reading JSON file {file_path}: {e}")
            raise

    @staticmethod
    def extract_title_from_url(url: str) -> str:
        try:
            parsed_url = urlparse(url)
            path_segments = [seg for seg in parsed_url.path.strip("//").split("/") if seg]

            if not path_segments:
                return ""

            title_segment = path_segments[1:]

            title = " ".join(title_segment)
            title = re.sub(r"[-_]", " ", title)
            title = re.sub(r"[^a-zA-Z0-9\s]", "", title)
            title = " ".join(word.capitalize() for word in title.split())

            return title if title else ""

        except Exception as e:
            LOGGER.warning(f"Error extracting title from URL {url}: {e}")
            return "Web Content"

    @staticmethod
    def clean_text_content(content: str) -> str:
        if not content:
            return ""

        cleaned = re.sub(r"\n+", "\n", content)
        cleaned = re.sub(r"[^\S\n]+", " ", cleaned)
        cleaned = re.sub(r"\s+([.,!?;:])", r"\1", cleaned)
        cleaned = re.sub(r"([.,!?;:])\1+", r"\1", cleaned)
        return cleaned.strip()

    def process_text_entries(self, text_entries: List[TextEntry]) -> List[ContextEntry]:
        processed_entries = []

        for item in text_entries:
            url = item.url
            content = item.content

            title = self.extract_title_from_url(url)
            cleaned_content = self.clean_text_content(content)

            if cleaned_content:
                formatted_content = f"<{title}>\n{cleaned_content}"
                processed_entries.append(ContextEntry(source_url=url, content=formatted_content, section_name=title))
            else:
                LOGGER.warning(f"Empty content after cleaning for URL: {url}")

        return processed_entries

    @staticmethod
    def _remove_duplicate_entries(entries: List[TextEntry]) -> List[TextEntry]:
        return list(set(entries))

    def process_json_file(self, file_path: str) -> List[ContextEntry]:
        LOGGER.info(f"Processing JSON file: {file_path}")

        text_entries = self.read_json_file(file_path)
        processed_context_entries = self.process_text_entries(text_entries)

        LOGGER.info(f"Processed {len(processed_context_entries)} URL-content pairs")
        return processed_context_entries
