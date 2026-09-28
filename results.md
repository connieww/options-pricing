Binomial (CRR), S=K=100, r=0.05, sigma=0.2, T=1:
  N=10    10.2534   error 0.1972
  N=50    10.4107   error 0.0399
  N=100   10.4306   error 0.0200
  N=500   10.4466   error 0.0040
  N=1000  10.4486   error 0.0020
  -> error scales as 1/N (vs 1/sqrt(N) for Monte Carlo)

# Results

Parameters: S = K = 100, r = 0.05, sigma = 0.20, T = 1.0, q = 0

## Closed form (Black-Scholes)
Call 10.4506
Put   5.5735

## Monte Carlo
100,000 paths, seed 42: 10.4205 +/- 0.047  (0.64 standard errors from exact)

Convergence study — 20 seeds per path count, mean absolute error:

| N | mean abs. error |
|---|---|
| 100 | 1.22587 |
| 300 | 0.89863 |
| 1,000 | 0.39398 |
| 3,000 | 0.21755 |
| 10,000 | 0.15666 |
| 30,000 | 0.07849 |
| 100,000 | 0.02612 |
| 300,000 | 0.02126 |
| 1,000,000 | 0.01230 |

Fitted slope in log-log space: **-0.5225** (theory: -0.5).
10,000x the paths gave 100x the accuracy, i.e. sqrt(10,000).

## Binomial (CRR)
| N | price | error |
|---|---|---|
| 10 | 10.2534 | 0.1972 |
| 50 | 10.4107 | 0.0399 |
| 100 | 10.4306 | 0.0200 |
| 500 | 10.4466 | 0.0040 |
| 1000 | 10.4486 | 0.0020 |

Error scales as 1/N, versus 1/sqrt(N) for Monte Carlo — ten times the steps for
one extra digit, against a hundred times the paths.

European put: [yours]
American put: [yours]
Early-exercise premium: [yours]

## Tests
10 passing — put-call parity (at-the-money and across five strikes), vol
monotonicity, deep-ITM and zero-vol limits, MC within 3 SE of closed form, MC
standard error scaling, American >= European put, American call = European call
without dividends, binomial convergence to closed form.

## Notes and observations
- Binomial convergence is not monotone between consecutive N — the price
  oscillates as the strike moves relative to node positions.
- The fitted slope of -0.5225 rather than exactly -0.5 reflects finite-sample
  noise in the mean error at each path count; more seeds would tighten it.
- A truncated edit left `binomial_put` without a return statement. Python returns
  None implicitly, so nothing failed at import or call time; the error surfaced
  later as a TypeError in an unrelated comparison. The test suite caught it
  within seconds.