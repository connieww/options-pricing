# Options Pricing Engine

Three independent methods for pricing European and American options, cross-validated
against one another.

## Methods

| Method | Handles | Convergence |
|---|---|---|
| Black-Scholes | European only | exact (closed form) |
| Binomial (CRR) | European + American | O(1/N) in steps |
| Monte Carlo | European, extends to path-dependent | O(1/sqrt(N)) in paths |

## Key result

Monte Carlo pricing error falls as N^(-0.52), measured by fitting a power law to
error against path count across five orders of magnitude (100 to 1,000,000 paths,
20 seeds each). Theory predicts -0.5. Increasing paths 10,000x reduced mean
absolute error from 1.226 to 0.0123 — a factor of 100, exactly sqrt(10,000).

![Monte Carlo convergence](analysis/convergence.png)

The binomial tree converges as 1/N, an order of magnitude cheaper per digit of
accuracy, but unlike Monte Carlo it does not extend to path-dependent payoffs.

## Validation

10 tests. The strongest is put-call parity, which follows from no-arbitrage rather
than from any model, so it must hold regardless of implementation. Also: Monte
Carlo within 3 standard errors of the closed form, binomial convergence to the
closed form, limiting behaviour at zero volatility and deep in-the-money, and the
classic result that an American call on a non-dividend-paying stock is worth
exactly its European equivalent.

Full numbers in [results.md](results.md).

## Running it

    pip install -r requirements.txt
    pytest -v
    python -m analysis.convergence

## Limitations

- **Constant volatility.** Real option markets show a volatility smile, so a single
  sigma cannot reprice a whole chain.
- **Log-normal returns.** Understates tail risk relative to observed markets.
- **No dividends** in the reported results (the code accepts a continuous yield q).
- The binomial tree assumes discrete time; American prices are approximations that
  improve with N.

## What I learned

- Monte Carlo's 1/sqrt(N) rate means accuracy is expensive: one more decimal place
  costs 100x the compute. That is why variance reduction matters more than raw path
  count, and it is the motivation for the antithetic and control-variate work I plan
  to add next.
- The -sigma^2/2 term in the GBM solution is not cosmetic. It is Ito's correction,
  and it exists because exp() is convex, so E[exp(X)] != exp(E[X]). Dropping it
  makes the simulated stock drift too fast.
- Numerical code fails silently. A wrong price is still a plausible-looking number,
  so the only defence is validating against something known independently — which is
  why put-call parity is a better test than comparing against my own output.

## Reference

Hull, *Options, Futures and Other Derivatives*.
