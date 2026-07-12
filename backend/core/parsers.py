import os
from abc import ABC, abstractmethod

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


class BaseParser(ABC):
    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        """Extract clean plain text from the document at file_path."""
        ...


class EpubParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        book = epub.read_epub(file_path)
        text_parts: list[str] = []

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                soup = BeautifulSoup(content, "html.parser")
                text_parts.append(soup.get_text(separator="\n", strip=True))

        return "\n\n".join(text_parts)