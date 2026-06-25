"""Tests for the scoring module — aggregate() and compute_total()."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.scoring import compute_total, aggregate


def _make_scores(logic=5, evidence=5, rebuttal=5, expression=5):
    return {
        "logic_score": logic,
        "evidence_score": evidence,
        "rebuttal_score": rebuttal,
        "expression_score": expression,
    }


class TestComputeTotal:
    def test_all_max(self):
        assert compute_total(_make_scores(10, 10, 10, 10)) == 10.0

    def test_all_min(self):
        assert compute_total(_make_scores(1, 1, 1, 1)) == 1.0

    def test_uneven(self):
        assert compute_total(_make_scores(8, 6, 7, 5)) == 6.5

    def test_mixed(self):
        assert compute_total(_make_scores(0, 10, 10, 0)) == 5.0


class TestAggregate:
    def test_empty_rounds(self):
        result = aggregate([])
        assert result["pro_score"] == 0
        assert result["con_score"] == 0
        assert result["winner"] == "平局"

    def test_pro_wins(self):
        rounds = [
            {"round": 1, "pro_scores": _make_scores(8, 8, 8, 8), "con_scores": _make_scores(5, 5, 5, 5)}
        ]
        result = aggregate(rounds)
        assert result["pro_score"] == 8
        assert result["con_score"] == 5
        assert result["winner"] == "pro"

    def test_con_wins(self):
        rounds = [
            {"round": 1, "pro_scores": _make_scores(4, 4, 4, 4), "con_scores": _make_scores(7, 7, 7, 7)}
        ]
        result = aggregate(rounds)
        assert result["pro_score"] == 4
        assert result["con_score"] == 7
        assert result["winner"] == "con"

    def test_draw(self):
        rounds = [
            {"round": 1, "pro_scores": _make_scores(6, 6, 6, 6), "con_scores": _make_scores(6, 6, 6, 6)}
        ]
        result = aggregate(rounds)
        assert result["winner"] == "平局"

    def test_multi_round_average(self):
        rounds = [
            {"round": 1, "pro_scores": _make_scores(8, 8, 8, 8), "con_scores": _make_scores(4, 4, 4, 4)},
            {"round": 2, "pro_scores": _make_scores(6, 6, 6, 6), "con_scores": _make_scores(6, 6, 6, 6)},
        ]
        result = aggregate(rounds)
        assert result["pro_score"] == 7
        assert result["con_score"] == 5

    def test_round_to_integer(self):
        rounds = [
            {"round": 1, "pro_scores": _make_scores(7, 7, 7, 7), "con_scores": _make_scores(6, 6, 6, 6)}
        ]
        result = aggregate(rounds)
        assert isinstance(result["pro_score"], int)
        assert isinstance(result["con_score"], int)
