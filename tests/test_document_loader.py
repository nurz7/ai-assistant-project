import tempfile
import unittest
from pathlib import Path

from app.services.document_loader import load_document_chunks


class DocumentLoaderTests(unittest.TestCase):
    def test_loads_sections_and_creates_deterministic_overlapping_chunks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_path = Path(temp_dir)
            (docs_path / "sample_methodology.md").write_text(
                "# Sample Methodology\n\n## First Section\n\n"
                "one two three four five six seven\n",
                encoding="utf-8",
            )

            chunks = load_document_chunks(
                docs_path,
                chunk_size_words=4,
                overlap_words=1,
            )

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].document, "sample_methodology.md")
        self.assertEqual(chunks[0].title, "Sample Methodology")
        self.assertEqual(chunks[0].section, "First Section")
        self.assertEqual(chunks[0].chunk_id, "sample-methodology-first-section-001")
        self.assertEqual(chunks[0].content, "one two three four")
        self.assertEqual(chunks[1].content, "four five six seven")

    def test_missing_document_directory_returns_empty_list(self) -> None:
        chunks = load_document_chunks(Path("missing-test-documents"))

        self.assertEqual(chunks, [])

    def test_rejects_invalid_chunk_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "overlap_words"):
                load_document_chunks(
                    Path(temp_dir),
                    chunk_size_words=10,
                    overlap_words=10,
                )
