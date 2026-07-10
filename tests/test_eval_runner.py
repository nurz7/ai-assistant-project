import unittest

from evals.run_evals import evaluate_dataset, load_dataset


class EvalRunnerTests(unittest.TestCase):
    def test_committed_dataset_has_at_least_twenty_cases(self) -> None:
        dataset = load_dataset()

        self.assertGreaterEqual(len(dataset["cases"]), 20)

    def test_committed_dataset_meets_quality_gates(self) -> None:
        report = evaluate_dataset()

        self.assertTrue(report["passed"], report["failures"])
