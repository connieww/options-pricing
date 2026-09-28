"""Validation tests for the pricing models."""

import numpy as np
from pricers.black_scholes import bs_call, bs_put


def test_put_call_parity():
    """C - P = S - K*exp(-rT). Pure no-arbitrage, must hold in any model."""
    S, K, r, sigma, T = 100, 100, 0.05, 0.2, 1.0
    lhs = bs_call(S, K, r, sigma, T) - bs_put(S, K, r, sigma, T)
    rhs = S - K * np.exp(-r * T)
    assert abs(lhs - rhs) < 1e-10


def test_parity_across_strikes():
    """The same identity at every strike, not just at-the-money."""
    S, r, sigma, T = 100, 0.05, 0.2, 1.0
    for K in [50, 80, 100, 120, 150]:
        lhs = bs_call(S, K, r, sigma, T) - bs_put(S, K, r, sigma, T)
        rhs = S - K * np.exp(-r * T)
        assert abs(lhs - rhs) < 1e-10, f"parity failed at K={K}"


def test_call_increases_with_volatility():
    """More vol means more upside optionality, so a call is worth more."""
    low = bs_call(100, 100, 0.05, 0.2, 1.0)
    high = bs_call(100, 100, 0.05, 0.4, 1.0)
    assert high > low


def test_deep_itm_call_approaches_intrinsic():
    """A call struck far below spot is nearly all intrinsic value."""
    price = bs_call(100, 10, 0.05, 0.2, 1.0)
    intrinsic = 100 - 10 * np.exp(-0.05 * 1.0)
    assert abs(price - intrinsic) < 0.01


def test_zero_volatility_is_discounted_intrinsic():
    """With no randomness the payoff is certain: max(S*e^rT - K, 0), discounted."""
    price = bs_call(100, 90, 0.05, 1e-9, 1.0)
    expected = max(100 - 90 * np.exp(-0.05), 0)
    assert abs(price - expected) < 0.01