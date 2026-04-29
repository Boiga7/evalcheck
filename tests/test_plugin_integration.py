"""End-to-end smoke tests — runs evalcheck under a real pytest invocation."""


def test_plain_pytest_passes_when_exact_match_meets_threshold(pytester):
    pytester.makepyfile(
        """
        from evalcheck import EvalOutput, eval, exact_match

        @eval(exact_match, threshold=1.0)
        def test_classifier():
            return EvalOutput(output="spam", expected="spam")
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_plain_pytest_fails_when_exact_match_below_threshold(pytester):
    pytester.makepyfile(
        """
        from evalcheck import EvalOutput, eval, exact_match

        @eval(exact_match, threshold=1.0)
        def test_classifier():
            return EvalOutput(output="spam", expected="ham")
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(failed=1)


def test_plain_pytest_runs_regex_match_with_kwargs(pytester):
    pytester.makepyfile(
        """
        from evalcheck import eval, regex_match

        @eval(regex_match, threshold=1.0, pattern=r"#\\d+")
        def test_extracts_order_id():
            return "order #1234 confirmed"
        """
    )
    result = pytester.runpytest()
    result.assert_outcomes(passed=1)


def test_dash_k_filter_works_normally(pytester):
    pytester.makepyfile(
        """
        from evalcheck import EvalOutput, eval, exact_match

        @eval(exact_match, threshold=1.0)
        def test_keep_me():
            return EvalOutput(output="hi", expected="hi")

        @eval(exact_match, threshold=1.0)
        def test_skip_me():
            return EvalOutput(output="hi", expected="hi")
        """
    )
    result = pytester.runpytest("-k", "keep")
    result.assert_outcomes(passed=1, deselected=1)
