from __future__ import annotations

import unittest

from src.metrics import evaluate_records, tool_call_rationality
from src.reward import RewardConfig


class MetricsTest(unittest.TestCase):
    def test_rational_search_call_scores_one(self) -> None:
        score, components = tool_call_rationality(
            "<search>capital of France</search><answer>Paris</answer>",
            requires_search=True,
            max_search_calls=2,
            search_relevance=[1.0],
        )
        self.assertAlmostEqual(score or 0.0, 1.0)
        self.assertEqual(components["necessity_alignment"], 1.0)

    def test_missing_required_search_scores_zero(self) -> None:
        score, _ = tool_call_rationality(
            "<answer>Paris</answer>",
            requires_search=True,
        )
        self.assertEqual(score, 0.0)

    def test_summary_contains_core_agentic_search_metrics(self) -> None:
        records = [
            {
                "id": "1",
                "ground_truth": "Paris",
                "requires_search": True,
                "search_relevance": [1.0],
                "output": "<search>capital France</search><answer>Paris</answer>",
            },
            {
                "id": "2",
                "ground_truth": "4",
                "requires_search": False,
                "output": "<answer>5</answer>",
            },
        ]
        _, summary = evaluate_records(records, RewardConfig())
        self.assertEqual(summary["samples"], 2)
        self.assertAlmostEqual(float(summary["accuracy"]), 0.5)
        self.assertAlmostEqual(float(summary["avg_search_turns"]), 0.5)
        self.assertAlmostEqual(float(summary["tool_call_rationality"]), 1.0)


if __name__ == "__main__":
    unittest.main()
