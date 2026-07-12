from unittest.mock import MagicMock, patch

import ebooklib
import pytest

from backend.core.chunker import chunk_text
from backend.core.parsers import EpubParser


def test_chunk_text():
    text = "word " * 5000
    chunks = chunk_text(text, chunk_size=2000, chunk_overlap=200)
    assert len(chunks) > 1, "Long text should be split into multiple chunks"
    overlap_found = any(chunks[0][-50:] in chunks[i] for i in range(1, len(chunks)))
    assert overlap_found, "Consecutive chunks should share overlapping content"


@pytest.fixture
def fake_book():
    book = MagicMock()
    html1 = b"<html><body><p>Chapter 1 content.</p></body></html>"
    html2 = b"<html><body><p>Chapter 2 content.</p></body></html>"

    item1 = MagicMock()
    item1.get_type.return_value = ebooklib.ITEM_DOCUMENT
    item1.get_content.return_value = html1

    item2 = MagicMock()
    item2.get_type.return_value = ebooklib.ITEM_DOCUMENT
    item2.get_content.return_value = html2

    book.get_items.return_value = [item1, item2]
    return book


@patch("backend.core.parsers.epub.read_epub")
def test_epub_parser_extract_text(mock_read_epub, fake_book, tmp_path):
    mock_read_epub.return_value = fake_book

    dummy_path = tmp_path / "dummy.epub"
    dummy_path.write_text("")

    parser = EpubParser()
    result = parser.extract_text(str(dummy_path))

    assert "Chapter 1 content." in result
    assert "Chapter 2 content." in result
    assert result == "Chapter 1 content.\n\nChapter 2 content."
    mock_read_epub.assert_called_once_with(str(dummy_path))
