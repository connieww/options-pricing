"""Black-Scholes closed-form pricing for European options."""

import numpy as np
from scipy.stats import norm


def _d1_d2(S, K, r, sigma, T, q=0.0):
    """
    d1 = [ln(S/K) + (r - q + sigma**2 / 2) * T] / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    """
    
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_call(S, K, r, sigma, T, q=0.0):
    """Call = S * exp(-q*T) * N(d1) - K * exp(-r*T) * N(d2)"""
    d1, d2 = _d1_d2(S, K, r, sigma, T, q)
    
    return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def bs_put(S, K, r, sigma, T, q=0.0):
    """Put = K * exp(-r*T) * N(-d2) - S * exp(-q*T) * N(-d1)"""
    d1, d2 = _d1_d2(S, K, r, sigma, T, q)

    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)



if __name__ == "__main__":
    S, K, r, sigma, T = 100, 100, 0.05, 0.2, 1.0
    print(f"Call: {bs_call(S, K, r, sigma, T):.4f}   (expect 10.4506)")
    print(f"Put:  {bs_put(S, K, r, sigma, T):.4f}   (expect 5.5735)")