# Options Pricing Engine

Three independent methods for pricing European and American options, built from
scratch and cross-validated against one another.

Written as a first-year CS student learning how derivatives pricing actually works.
---

## Key result

Monte Carlo pricing error falls as **N^(-0.52)**, measured by fitting a power law to
error against path count across five orders of magnitude (100 to 1,000,000 paths,
20 seeds each). The mathematical theory predicts -0.5.

Increasing paths 10,000x reduced mean absolute error from 1.226 to 0.0123 — a factor
of 100, exactly sqrt(10,000).

![Monte Carlo convergence](analysis/convergence.png)

The binomial tree converges as 1/N — an order of magnitude cheaper per digit of
accuracy — but unlike Monte Carlo it does not extend to path-dependent payoffs.

---

## What an option actually is
The clearest way I found to think about it:

- I sell you, for **$20 today**, the **right** — not the obligation — to buy a concert
  ticket from me at **$100 on June 1st**.
- Artist blows up, tickets resell at $300 → you use the right, pay $100, you're ahead.
- Artist flops, tickets resell at $40 → you walk away. You lose only the $20.
- That $20 is the **premium**. Computing it is what this project does.
- $100 is the **strike**. June 1st is the **expiry**.

**European vs American:**
- **European** — usable only *on* the expiry date.
- **American** — usable any time up to it.
- More choice can't hurt you, so American >= European always. This repo measures that
  gap directly (the *early-exercise premium*), and one test asserts the inequality.

**What the price depends on:**

| Input | In the analogy | Observable? |
|---|---|---|
| S — spot price | what tickets go for now | yes |
| K — strike | the agreed $100 | yes |
| T — time to expiry | months until June 1st | yes |
| r — risk-free rate | what cash earns meanwhile | yes |
| **sigma — volatility** | **how wildly popularity swings** | **no** |

Four of five you can look up. Volatility you cannot — nobody knows how much the
artist's popularity will swing. **That single unobservable input is the whole
difficulty of the field.**

---

## Why anyone needs this priced accurately

- Quant firms are mostly **market makers**: they quote a price to buy (bid) and a price
  to sell (ask) at the same time, simultaneously.
- They earn the **spread** — the gap between the two — thousands of times a day.
- The spread is thin. **A pricing error wider than the spread eats the entire margin.**
- So the value isn't in predicting where the stock goes. It's in being able to quote
  a price that's right, fast, every time.

---

## The three models, and the maths behind them

All three answer the same question:

> **price = e^(-rT) x E[payoff at expiry]**

The expected payoff, discounted back to today. They differ only in how they evaluate
that expectation.

### 1. Black-Scholes — solve the integral by hand

- **Assumes** the stock follows geometric Brownian motion: `dS = mu*S*dt + sigma*S*dW`.
  Proportional moves, not absolute ones — a 2% day is a 2% day at $10 or $1,000.
- Applying **Ito's lemma** to ln(S) turns that into something with constant
  coefficients, which integrates to:

      S_T = S_0 * exp((mu - sigma^2/2)*T + sigma*sqrt(T)*Z),   Z ~ N(0,1)

- The `-sigma^2/2` is **Ito's correction**. It exists because exp() is convex, so
  E[exp(X)] != exp(E[X]) — without it the simulated stock drifts too fast.
- **Risk-neutral pricing:** because the option can be replicated by continuously
  trading the stock and cash, its price can't depend on anyone's view of the stock's
  return. So we set mu = r - q and price as if everyone were indifferent to risk.
  **The option's value depends on how much the stock moves, not which way.**
- S_T is then log-normal, the expectation has a closed form, and you get:

      Call = S*e^(-qT)*N(d1) - K*e^(-rT)*N(d2)
      d1 = [ln(S/K) + (r - q + sigma^2/2)T] / (sigma*sqrt(T));   d2 = d1 - sigma*sqrt(T)

- **Reading it:** N(d2) is the risk-neutral probability of finishing in the money.
  K*e^(-rT)*N(d2) is the expected discounted cost of paying the strike. S*e^(-qT)*N(d1)
  is the expected discounted value of the stock you receive. What you get minus what
  you pay, each probability-weighted.
- **Cost:** instant. **Limit:** European only — it has no way to represent a decision
  made partway through.

### 2. Binomial tree (Cox-Ross-Rubinstein) — enumerate the futures

- Chop time into N steps. Each step the stock multiplies by `u` or `d`:

      u = exp(sigma*sqrt(dt)),   d = 1/u,   p = (exp((r-q)*dt) - d) / (u - d)

- `p` is again a **risk-neutral** probability, not a real-world one: it's the value
  that makes the stock drift at the risk-free rate.
- Compute payoffs at every terminal node, then **work backwards**: each node's value
  is the discounted expected value of the two nodes it leads to.
- **American options fall out naturally.** At every node, compare:

      continuation = discounted expected value of waiting
      intrinsic    = what you'd get exercising right now
      value        = max(continuation, intrinsic)

  You cannot do this in a formula, because it's a decision at every point in time.
- **Cost:** O(1/N) error. **Limit:** struggles with path-dependence and multiple assets.

### 3. Monte Carlo — sample the futures

- Draw many random Z's, push each through the GBM solution, compute each payoff,
  average, discount.
- **Law of large numbers** says the average converges to the true expectation.
- **Central limit theorem** says how fast: the standard error of a mean is
  `sd / sqrt(n)`. That is exactly where the 1/sqrt(N) rate comes from — it isn't a
  property of options, it's a property of averaging.
- **Cost:** O(1/sqrt(N)) — expensive. **Reach:** the widest. It doesn't care how
  complicated the payoff is, only that you can simulate it.

---

## Why a firm needs all three

| | Black-Scholes | Binomial | Monte Carlo |
|---|---|---|---|
| Speed | instant | fast | slow |
| Error | exact | O(1/N) | O(1/sqrt(N)) |
| European | yes | yes | yes |
| American / early exercise | **no** | **yes** | awkward |
| Path-dependent (Asian, barrier) | no | no | **yes** |
| Multi-asset | no | poorly | **yes** |
| Stochastic vol, jumps | no | no | **yes** |

- **Black-Scholes** is the quoting language. Options trade in *volatility*, not dollars,
  and Black-Scholes is the dictionary between the two. Nobody believes its assumptions —
  it's used as a units converter, the way bonds are quoted in yield.
- **Binomial** is what you reach for the moment early exercise matters.
- **Monte Carlo** is what survives when the payoff or the model gets complicated enough
  that no formula exists.

---

## The misconception I had to correct

I initially believed Monte Carlo was a *more realistic* model that catches what
Black-Scholes misses. **That's wrong, and the error is worth naming.**

- All three methods assume **the same story** about how prices move.
- Black-Scholes solves that story exactly. Monte Carlo approximates the same story by
  sampling. It's the difference between computing 5! = 120 and writing out all 120
  arrangements and counting them — **counting isn't more accurate, it's just slower and
  can miscount.**
- For a plain European option Monte Carlo is **strictly worse**: slower, and it carries
  sampling error (my +/- 0.047) that the formula doesn't have.
- This repo proves it: `test_mc_matches_bs` asserts the two agree. If Monte Carlo were
  catching something extra, that test would fail. It passes every time, and the
  convergence plot shows Monte Carlo *approaching* Black-Scholes, not correcting it.
- **Realism comes from changing the model** (stochastic volatility, jumps), not from the
  method. Richer models usually have no closed form — which is *why* they're priced by
  simulation. Monte Carlo is the tool that survives complicated models. It doesn't
  supply the realism itself.

---

## Betting with a backup: how the pricing gets used

- A market maker sells you the ticket-right at $21 and buys at $19, pocketing the spread.
- But if she sells you the right and the artist blows up, she owes you a $300 ticket
  for $100. That's a real risk she doesn't want.
- So the moment she sells, **she buys a calculated fraction of actual tickets.** That
  fraction is **delta** — the sensitivity of the option price to the stock price, the
  slope of price against strike.
- Artist blows up: she loses on the option, wins on the tickets.
  Artist flops: she wins on the option, loses on the tickets.
- **Direction cancels. The spread remains.** That's **delta hedging**, and it's why
  accuracy matters more than prediction.

**The insurance framing:** an option is a **contingent claim** — an uncertain future
payout. Pricing one means finding the probability distribution of that payout and
discounting its expectation to today. That is structurally identical to actuarial
pricing, which is what drew me to this: the option premium is a policy premium, and
sigma plays the role of claim variance.

**The poker framing:** none of this is prediction. It's making many small positive-EV
bets, sized so no single one is ruinous, and letting the law of large numbers work.
Hedging is the extra step that strips out even the luck of the draw — which is why
quant firms recruit from poker and estimation games rather than from forecasters.

---

## Results

Parameters: S = K = 100, r = 0.05, sigma = 0.20, T = 1.0, q = 0

| Method | Price | Note |
|---|---|---|
| Black-Scholes call | 10.4506 | exact |
| Black-Scholes put | 5.5735 | exact |
| Monte Carlo (100k paths, seed 42) | 10.4205 +/- 0.047 | 0.64 SE from exact |
| Binomial, N = 1000 | 10.4486 | error 0.0020 |

Binomial convergence:

| N | price | error |
|---|---|---|
| 10 | 10.2534 | 0.1972 |
| 50 | 10.4107 | 0.0399 |
| 100 | 10.4306 | 0.0200 |
| 500 | 10.4466 | 0.0040 |
| 1000 | 10.4486 | 0.0020 |

Error falls as 1/N. Compare Monte Carlo's 1/sqrt(N): ten times the tree steps for one
extra digit, against a hundred times the simulation paths.

Full numbers and working notes in [results.md](results.md).

---

## Validation

10 tests. The design principle: **a test is only worth writing if it checks against
something known independently of the implementation.** Asserting my own output back at
itself proves nothing.

- **Put-call parity**, at-the-money and across five strikes. This follows from
  no-arbitrage alone, not from any model, so it must hold regardless of implementation.
  It's the strongest test in the suite.
- **Monte Carlo within 3 standard errors** of the closed form.
- **Standard error scaling** — quadrupling paths roughly halves the error.
- **Binomial convergence** to the closed form at N = 2000.
- **Limiting cases** — zero volatility collapses to discounted intrinsic value; deep
  in-the-money approaches a forward.
- **American >= European put**, since an extra right can't reduce value.
- **American call = European call without dividends** — the classic result that early
  exercise of a call is never optimal, verified to twelve decimal places.

---

## Sanity checks and intuition

Varying one input at a time, and checking the behaviour is sensible rather than merely
numerical:

- **Volatility.** Price rises with sigma but not linearly, and sensitivity peaks
  at-the-money — which is where uncertainty about finishing in or out of the money is
  greatest. (This is *vega*.)
- **Strike.** Price traces an S-curve: nearly 1-for-1 with spot deep in the money,
  flattening to zero far out. The slope is *delta*, which is also the hedge ratio.
- **Time.** More time is usually worth more — but **not always**. For a deep
  in-the-money put, a longer expiry can be worth *less*: you're delaying a payoff you're
  already fairly certain of, and discounting eats it. This is precisely why American
  puts get exercised early while American calls don't.
- **Rates.** Calls rise with r, puts fall. A call defers paying the strike, and deferring
  a payment is worth more when money earns more.

---

## Assumptions, and where they break

| Assumption | Why it's made | How reality differs | Effect on price |
|---|---|---|---|
| Constant volatility | makes the integral solvable | implied vol varies by strike (the smile) | underprices tails, especially far OTM |
| Log-normal returns | keeps prices positive, maths tractable | real returns have fat tails | understates crash risk |
| Continuous trading, no costs | required for the replication argument | spreads, fees, discrete hedging | the hedge is imperfect |
| No dividends (in my results) | one fewer parameter | most large stocks pay them | overprices calls, underprices puts |
| Known, constant r | simplifies discounting | rates move | minor for short expiries |

**The most important one is constant volatility, and the market openly disagrees with
it.** The existence of the volatility smile — different implied vols at different
strikes — is the market pricing in exactly the fat tails this model rules out.

---

## When this is useful, and when it isn't

**Reasonable:** liquid, short-dated, near-the-money European options on non-dividend
stocks. Sanity-checking a quote. Building intuition for how the Greeks behave.

**Poor:** long-dated options (volatility won't stay constant for five years), deep
out-of-the-money options (exactly where the log-normal assumption fails), anything in a
regime shift, and any path-dependent payoff — which needs the Monte Carlo engine
extended, not just reused.

---

## What I learned

- **The 1/sqrt(N) rate is a tax on accuracy.** One extra decimal place costs 100x the
  compute. That's why variance reduction matters more than raw path count, and it's the
  motivation for the antithetic and control-variate work I'm adding next.
- **The -sigma^2/2 term is not cosmetic.** It's Ito's correction, and it exists because
  exp() is convex. Drop it and the simulation drifts too fast — the median path and the
  mean path are genuinely different things, which is also why volatility drags returns.
- **Numerical code fails silently.** A wrong price is still a plausible-looking number.
  There's no crash, no red text. The only defence is validating against something known
  independently — which is why put-call parity is a better test than any comparison
  against my own output.
- **A concrete instance of that:** a truncated edit left `binomial_put` with no return
  statement. Python returns None implicitly, so nothing failed at import or call time;
  the error surfaced much later as a TypeError in an unrelated comparison. The test
  suite caught it within seconds, and the *pattern* of which tests failed isolated it to
  one function before I read any code.
- **Convergence isn't always monotone.** The binomial price oscillates above and below
  the true value between consecutive N, as the strike moves relative to node positions.
  Knowing this stops you "tuning" N to whichever value happens to look best.
- **The models aren't rivals.** I came in thinking one must be better. They're the same
  model computed three ways, with different costs and different reach. Choosing between
  them is an engineering decision, not a search for truth.

---

## Next steps

- [ ] **Implied volatility solver** — invert Black-Scholes numerically (bisection or
      Newton-Raphson) to back out sigma from real market prices
- [ ] **Plot the volatility smile** from a live option chain, demonstrating the
      constant-volatility assumption failing on real data
- [ ] **Variance reduction** — antithetic and control variates, measured at equal
      wall-clock time
- [ ] **Greeks** — delta and vega by finite difference, validated against analytic values
- [ ] **C++ port** of the pricing core, with Python retained for analysis and plotting

---

## Running it

    pip install -r requirements.txt
    pytest -v
    python -m analysis.convergence

---

## Reference

Hull, *Options, Futures and Other Derivatives* — standard reference for the
Black-Scholes derivation and the CRR parameterisation.
