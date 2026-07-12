import tempfile
import unittest
from pathlib import Path

from app.services.retrieval_service import retrieve_relevant_chunks


class RetrievalServiceTests(unittest.TestCase):
    def test_retrieves_relevant_methodology_section(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            docs_path = Path(temp_dir)
            (docs_path / "water_detection.md").write_text(
                "# Water Detection\n\n## MNDWI Water Mask\n\n"
                "MNDWI is used for water surface detection in reservoir scenes.\n\n"
                "## Cloud Filtering\n\nCloud filtering flags low confidence scenes.\n",
                encoding="utf-8",
            )

            results = retrieve_relevant_chunks(
                "What is MNDWI used for in water surface detection?",
                docs_path=docs_path,
            )

        self.assertTrue(results)
        self.assertEqual(results[0].chunk.section, "MNDWI Water Mask")
        self.assertGreaterEqual(results[0].score, 0.35)

    def test_refuses_query_without_matching_context(self) -> None:
        results = retrieve_relevant_chunks(
            "What was the exact water level of unknown reservoir X on 2020-01-01?",
        )

        self.assertEqual(results, [])

    def test_demo_mndwi_question_returns_expected_source(self) -> None:
        results = retrieve_relevant_chunks(
            "What is MNDWI used for in water surface detection?"
        )

        self.assertTrue(results)
        self.assertEqual(results[0].chunk.document, "sentinel2_water_detection.md")
        self.assertEqual(results[0].chunk.section, "MNDWI Water Mask")

    def test_retrieves_russian_thesis_methodology_question(self) -> None:
        results = retrieve_relevant_chunks(
            "Как выполняется автоматический контроль качества временных рядов воды?"
        )

        self.assertTrue(results)
        self.assertEqual(results[0].chunk.document, "thesis_satellite_pipeline.md")
        self.assertEqual(results[0].chunk.section, "Automatic Quality Control")

    def test_refuses_russian_exact_water_level_question(self) -> None:
        results = retrieve_relevant_chunks(
            "Какой точный уровень воды был в неизвестном водоеме?"
        )

        self.assertEqual(results, [])
