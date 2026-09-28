"""Measure and plot Monte Carlo convergence: error vs number of paths."""

import numpy as np
import matplotlib.pyplot as plt

from pricers.black_scholes import bs_call
from pricers.monte_carlo import mc_call

S, K, r, sigma, T = 100, 100, 0.05, 0.2, 1.0
EXACT = bs_call(S, K, r, sigma, T)

PATH_COUNTS = [100, 300, 1_000, 3_000, 10_000, 30_000,
               100_000, 300_000, 1_000_000]
N_TRIALS = 20        # average over seeds so the curve isn't noise


def measure_errors():
    """Return mean absolute pricing error at each path count."""
    mean_errors = []

    for n in PATH_COUNTS:
        errors = []                                  # ← create it here, fresh per n
        for seed in range(N_TRIALS):
            price, _ = mc_call(S, K, r, sigma, T, n_paths=n, seed=seed)
            errors.append(abs(price - EXACT))
        mean_errors.append(np.mean(errors))          # ← one number per path count

    return np.array(mean_errors)


def main():
    errors = measure_errors()
    ns = np.array(PATH_COUNTS, dtype=float)

    # Fit a straight line in log-log space: log(error) = slope * log(n) + c
    slope, intercept = np.polyfit(np.log(ns), np.log(errors), 1)
    fitted = np.exp(intercept) * ns**slope

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.loglog(ns, errors, "o", markersize=7, color="#2563eb",
              label="Measured error")
    ax.loglog(ns, fitted, "-", linewidth=2, color="#64748b",
              label=f"Fit: slope = {slope:.3f}")

    ax.set_xlabel("Number of paths (N)")
    ax.set_ylabel("Mean absolute pricing error")
    ax.set_title("Monte Carlo convergence: error falls as $1/\\sqrt{N}$")
    ax.grid(True, which="both", linewidth=0.5, alpha=0.3)
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig("analysis/convergence.png", dpi=150)
    print(f"Fitted slope: {slope:.4f}   (theory predicts -0.5)")
    for n, e in zip(PATH_COUNTS, errors):
        print(f"  N = {n:>9,}:  mean |error| = {e:.5f}")


if __name__ == "__main__":
    main()
