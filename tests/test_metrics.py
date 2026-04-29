"""Tests for evalcheck metrics."""

from evalcheck import exact_match, regex_match


def test_exact_match_returns_one_when_strings_are_identical():
    assert exact_match(output="hello", expected="hello") == 1.0


def test_exact_match_returns_zero_when_strings_differ():
    assert exact_match(output="hello", expected="goodbye") == 0.0


def test_regex_match_returns_one_when_pattern_matches():
    assert regex_match(output="order #12345 confirmed", pattern=r"#\d+") == 1.0


def test_regex_match_returns_zero_when_pattern_does_not_match():
    assert regex_match(output="no order number here", pattern=r"#\d+") == 0.0


def test_regex_match_anchors_full_match_when_requested():
    assert regex_match(output="hello world", pattern=r"hello", full_match=True) == 0.0
    assert regex_match(output="hello", pattern=r"hello", full_match=True) == 1.0
