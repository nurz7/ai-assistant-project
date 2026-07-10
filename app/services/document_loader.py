import re
from pathlib import Path

from app.models.documents import DocumentChunk

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
SLUG_PATTERN = re.compile(r"[^a-z0-9]+")


def _slugify(value: str) -> str:
    slug = SLUG_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "section"


def _split_sections(
    content: str, fallback_title: str
) -> tuple[str, list[tuple[str, str]]]:
    title = fallback_title
    current_section = "Overview"
    current_lines: list[str] = []
    sections: list[tuple[str, str]] = []

    def flush_section() -> None:
        section_content = "\n".join(current_lines).strip()
        if section_content:
            sections.append((current_section, section_content))
        current_lines.clear()

    for line in content.splitlines():
        heading = HEADING_PATTERN.match(line)
        if not heading:
            current_lines.append(line)
            continue

        level = len(heading.group(1))
        heading_text = heading.group(2).strip()
        if level == 1:
            title = heading_text
            continue

        flush_section()
        current_section = heading_text

    flush_section()
    return title, sections


def _chunk_words(text: str, chunk_size_words: int, overlap_words: int) -> list[str]:
    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive")
    if overlap_words < 0 or overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be between 0 and chunk_size_words - 1")

    words = text.split()
    if not words:
        return []

    step = chunk_size_words - overlap_words
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += step

    return chunks


def load_document_chunks(
    docs_path: Path,
    *,
    chunk_size_words: int = 120,
    overlap_words: int = 20,
) -> list[DocumentChunk]:
    """Load Markdown methodology files into deterministic section chunks."""

    if chunk_size_words <= 0:
        raise ValueError("chunk_size_words must be positive")
    if overlap_words < 0 or overlap_words >= chunk_size_words:
        raise ValueError("overlap_words must be between 0 and chunk_size_words - 1")

    if not docs_path.exists() or not docs_path.is_dir():
        return []

    chunks: list[DocumentChunk] = []
    for document_path in sorted(docs_path.glob("*.md")):
        content = document_path.read_text(encoding="utf-8")
        fallback_title = document_path.stem.replace("_", " ").title()
        title, sections = _split_sections(content, fallback_title)
        chunk_number = 0

        for section, section_content in sections:
            for chunk_content in _chunk_words(
                section_content,
                chunk_size_words,
                overlap_words,
            ):
                chunk_number += 1
                chunk_id = (
                    f"{_slugify(document_path.stem)}-"
                    f"{_slugify(section)}-{chunk_number:03d}"
                )
                chunks.append(
                    DocumentChunk(
                        document=document_path.name,
                        title=title,
                        section=section,
                        chunk_id=chunk_id,
                        content=chunk_content,
                    )
                )

    return chunks
