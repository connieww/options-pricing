"""Monte Carlo pricing of European options under geometric Brownian motion."""
"""Monte Carlo simulation is a numerical method that uses random sampling to estimate the expected value of a function. 
In the context of option pricing, it can be used to simulate the evolution of the underlying asset price and calculate the expected payoff of an option."""

import numpy as np

"""right to buy the asset at strike K"""
def mc_call(S, K, r, sigma, T, n_paths=100_000, q=0.0, seed=None):
    """
    Price a European call by simulation.

    Terminal price under risk-neutral GBM:
        S_T = S * exp((r - q - sigma**2 / 2) * T + sigma * sqrt(T) * Z),  Z ~ N(0,1)

    Payoff:  max(S_T - K, 0)
    Price:   exp(-r*T) * mean(payoff)

    Returns
    -------
    (price, standard_error)
    """
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    
    S_T = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    payoffs = np.maximum(S_T - K, 0.0)
    discounted = np.exp(-r * T) * payoffs
    return discounted.mean(), discounted.std(ddof=1) / np.sqrt(n_paths)


"""right to sell the asset at strike K"""
def mc_put(S, K, r, sigma, T, n_paths=100_000, q=0.0, seed=None):
    """Same, but the payoff is max(K - S_T, 0)."""
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal(n_paths)
    
    S_T = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    payoffs = np.maximum(K - S_T, 0.0)
    discounted = np.exp(-r * T) * payoffs
    return discounted.mean(), discounted.std(ddof=1) / np.sqrt(n_paths)


if __name__ == "__main__":
    price, se = mc_call(100, 100, 0.05, 0.2, 1.0, n_paths=100_000, seed=42)
    print(f"MC call: {price:.4f} +/- {se:.4f}   (BS exact: 10.4506)")

