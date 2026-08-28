from __future__ import annotations

import unittest

from src.reward import (
    RewardConfig,
    analyze_search_calls,
    load_reward_config,
    exact_match,
    extract_answer,
    score_trajectory,
)


class RewardTest(unittest.TestCase):
    def test_named_variant_has_builtin_efficiency_defaults(self) -> None:
        config = load_reward_config("outcome_efficiency")
        self.assertGreater(config.search_cost, 0.0)
        self.assertEqual(config.prm_weight, 0.0)

    def test_extracts_last_answer_and_accepts_aliases(self) -> None:
        output = "<answer>draft</answer><answer>Barack Obama</answer>"
        self.assertEqual(extract_answer(output), "Barack Obama")
        self.assertTrue(exact_match("The Barack Obama!", {"target": ["Barack Obama"]}))

    def test_search_statistics_include_invalid_and_duplicate_calls(self) -> None:
        output = "<search>capital France</search><search>capital France</search><search></search><search>open"
        stats = analyze_search_calls(output)
        self.assertEqual(stats.search_count, 2)
        self.assertEqual(stats.duplicate_count, 1)
        self.assertEqual(stats.invalid_count, 2)

    def test_outcome_efficiency_penalizes_redundant_search(self) -> None:
        config = RewardConfig(
            search_cost=0.05,
            duplicate_search_penalty=0.05,
            invalid_search_penalty=0.1,
        )
        output = "<search>a</search><search>a</search><answer>Paris</answer>"
        result = score_trajectory("nq", output, {"target": "Paris"}, config=config)
        self.assertAlmostEqual(result.outcome_reward, 1.0)
        self.assertAlmostEqual(result.efficiency_reward, -0.1)
        self.assertAlmostEqual(result.total, 0.9)

    def test_prm_uses_real_supplied_process_scores(self) -> None:
        config = RewardConfig(prm_weight=0.2)
        result = score_trajectory(
            "nq",
            "<think>step</think><answer>Paris</answer>",
            "Paris",
            {"process_scores": [0.6, 0.8]},
            config,
        )
        self.assertAlmostEqual(result.raw_prm_score or 0.0, 0.7)
        self.assertAlmostEqual(result.process_reward, 0.14)
        self.assertAlmostEqual(result.total, 1.14)

    def test_prm_fails_closed_without_scores_or_endpoint(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "no process scores"):
            score_trajectory(
                "nq",
                "<answer>Paris</answer>",
                "Paris",
                config=RewardConfig(prm_weight=0.2),
            )


if __name__ == "__main__":
    unittest.main()
