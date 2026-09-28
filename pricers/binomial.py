"""Cox-Ross-Rubinstein binomial tree pricing."""

import numpy as np


def binomial_call(S, K, r, sigma, T, N=100, q=0.0, american=False):
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    j = np.arange(N + 1)
    S_T = S * u**j * d**(N - j)
    V = np.maximum(S_T - K, 0.0)

    for i in range(N - 1, -1, -1):            
        V = disc * (p * V[1:] + (1 - p) * V[:-1])
        if american:                          
            j = np.arange(i + 1)
            S_i = S * u**j * d**(i - j)
            V = np.maximum(V, S_i - K)        

    return V[0]


def binomial_put(S, K, r, sigma, T, N=100, q=0.0, american=False):
    """Same as binomial_call, with terminal values max(K - S_T, 0)."""
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1.0 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    j = np.arange(N + 1)
    S_T = S * u**j * d**(N - j)
    V = np.maximum(K - S_T, 0.0)

    for i in range(N - 1, -1, -1):
        V = disc * (p * V[1:] + (1 - p) * V[:-1])
        if american:
            j = np.arange(i + 1)
            S_i = S * u**j * d**(i - j)
            V = np.maximum(V, K - S_i)

    return V[0]


if __name__ == "__main__":                    
    euro = binomial_put(100, 100, 0.05, 0.2, 1.0, N=1000, american=False)
    amer = binomial_put(100, 100, 0.05, 0.2, 1.0, N=1000, american=True)
    print(f"European put: {euro:.4f}   (BS exact: 5.5735)")
    print(f"American put: {amer:.4f}")
    print(f"Early-exercise premium: {amer - euro:.4f}")