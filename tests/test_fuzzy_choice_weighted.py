import pytest
from collections import Counter

from factory import fuzzy
from factory import random


def calculate_empirical_probabilities(samples, choices):
    unique_elements = list(dict.fromkeys(choices))
    total_samples = len(samples)
    counts = Counter(samples)
    probabilities = {elem: counts.get(elem, 0) / total_samples for elem in unique_elements}
    return probabilities


def calculate_expected_weights(choices):
    counts = Counter(choices)
    total = len(choices)
    weights = {elem: count / total for elem, count in counts.items()}
    return weights


def verify_statistical_significance(empirical_probs, expected_weights, tolerance=0.05):
    for elem in expected_weights:
        empirical = empirical_probs.get(elem, 0)
        expected = expected_weights[elem]
        if abs(empirical - expected) > tolerance:
            return False
    return True


@pytest.mark.parametrize("choices,num_samples,tolerance", [
    pytest.param(
        [1, 1, 2, 2, 3],
        10000,
        0.05,
        id="small_choices_5_elements"
    ),
    pytest.param(
        list(range(500)) + list(range(500)),
        50000,
        0.02,
        id="large_choices_1000_elements"
    ),
])
def test_fuzzy_choice_weighted_distribution(choices, num_samples, tolerance):
    random.reseed_random(42)

    fuzzy_choice = fuzzy.FuzzyChoice(choices)

    samples = []
    for _ in range(num_samples):
        samples.append(fuzzy_choice.fuzz())

    empirical_probs = calculate_empirical_probabilities(samples, choices)
    expected_weights = calculate_expected_weights(choices)

    assert verify_statistical_significance(empirical_probs, expected_weights, tolerance), (
        f"Empirical probabilities do not match expected weights within tolerance {tolerance}.\n"
        f"Expected: {expected_weights}\n"
        f"Empirical: {empirical_probs}"
    )
