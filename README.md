# Options Pricing Engine

Three ways of pricing the same option — Black Scholes Model, Monte
Carlo simulation and the Binary tree model — built from scratch and used to check each other.

Freshman CS project :)

---

## Why three methods

Although the mathematical formula for options pricing already exists _(i.e. the Black-Scholes Model)_, it is completely theoretical and uses closed-form solutions where variables remain uninfluenced. _Monte Carlo simulation_ bridges this gap by introducing real-world complexity. While Black-Scholes requires rigid assumptions—like constant volatility and predictable price paths—to make its neat equations work, Monte Carlo replaces strict formulas with thousands of simulated market paths. This flexibility allows financial analysts to accurately price complex, path-dependent "exotic" options and easily incorporate shifting interest rates, dividend changes, and erratic market volatility that rigid formulas simply cannot handle. 

While the _binomial tree model_ provides a flexible step-by-step framework for pricing American and path-dependent options, it also acts as a vital tool for cross-validation alongside Monte Carlo simulations. By comparing the numerical outputs of both models against the exact theoretical baseline of the Black-Scholes model for a standard option, analysts can audit their simulation algorithms, ensure consistency across random variables, and catch potential coding errors before pricing live assets.

The three models share almost nothing:

| Method | How it computes | Its error | What only it can do |
|---|---|---|---|
| Black-Scholes | closed-form algebra | none (exact) | instant pricing |
| Binomial (CRR) | enumerates a discrete lattice | discretisation, O(1/N) | American options early exercise |
| Monte Carlo | samples random outcomes | sampling, O(1/√N) | path-dependent payoffs |

Because a coding bug in the tree's backward induction cannot replicate inside a vectorized simulation, independent agreement across three distinct models provides robust evidence of code accuracy. These frameworks only overlap when pricing a standard European option, which is why this project values the simplest contract three ways to verify a baseline agreement. Once this test case confirms the computational engine is flawless, each specialized pricing method can be confidently deployed where the others fail.

So if Monte Carlo disagree with Black-Scholes : my code is wrong.
But if all three models agree but disagree with the market : the model is wrong.

---

## The maths, briefly

The variables used are here:
### Notation

| Symbol | Meaning | Units |
|---|---|---|
| S | current stock price (spot) | currency |
| K | strike price | currency |
| T | time to expiry | years |
| r | risk-free interest rate | per year, continuously compounded |
| q | dividend yield | per year, continuously compounded |
| σ | volatility | per √year |
| N | number of paths (Monte Carlo) or steps (binomial) | count |
| Z | standard normal random draw, Z ~ N(0,1) | — |
| N(·) | standard normal cumulative distribution function | — |
| S_T | stock price at expiry | currency |
| dt | length of one time step, T/N (binomial) | years |
| u, d | up and down factors per step (binomial) | multiplier |
| p | risk-neutral probability of an up-move (binomial) | probability |

All rates are decimals, not percentages: r = 0.05 means 5%. σ carries units of per √year
because variance scales with time, so standard deviation scales with √time — which is also
why √T rather than T appears in the formulas. Note that `N` does double duty: `N(d₁)` is the normal CDF, while a bare `N` is a step or
path count.

**All three compute `price = e^(-rT) × E[payoff]` — the expected payoff, discounted. They
differ in how they evaluate the expectation.**

### Black-Scholes Model
Assumes the stock follows geometric Brownian motion. Applying Ito's
lemma to ln(S) and integrating gives:

    S_T = S₀ · exp((r - q - σ²/2)T + σ√T · Z),   Z ~ N(0,1)

The `-σ²/2` is Ito's correction, and is there because exp() is convex, so E[exp(X)] ≠ exp(E[X]).
Because you can perfectly mimic the option using a dynamic mix of stock and cash, its price ignores market direction (\[\mu \]) and relies solely on volatility (\[\sigma \]). Since future stock prices follow a predictable log-normal distribution, the calculus for the expected payout simplifies cleanly into the standard Black-Scholes formula using \(N(d_1)\) and \(N(d_2)\).


### Binomial tree Approach
Chops time into N segments where the stock multiplies by
    u = exp(σ√dt)` or `d = 1/u`, with risk-neutral up-probability
    OR
    p = (exp((r-q)dt) - d)/(u - d). 
    
Since the payoff is known at expiry, start there and work backwards, each node being the discounted average of the two it leads to, until the tree
collapses to today's price.

This is why the tree handles American options: at every node you already know the continuation value (holding on) and the intrinsic value (exercising now), so taking `max`of the two prices the right to exercise early, which is a decision made at every point in time, which a formula has nowhere to represent.

### Monte Carlo Simulation
Draw many independent Z's from a standard normal distribution, push each one through the geometric Brownian motion solution to get a possible price at expiry, compute the payoff in each case, then average them and discount back to present. The **law of large numbers** guarantees that average converges to the true expected payoff as you add draws (increase N), and the **central limit theorem** tells you how fast it does so, since the standard error of a sample mean is `sd/√n`. 
The 1/√N rate has nothing to do with options. It's what happens whenever you estimate an average from a random sample: measure 100 people's heights and your estimate is off by some amount; measure 10,000 and it's only 10 times better, not 100.


---

## Results

S = K = 100, r = 0.05, σ = 0.20, T = 1.0, q = 0

| Method | Price | vs closed form |
|---|---|---|
| Black-Scholes call | 10.4506 | exact |
| Binomial, N = 1000 | 10.4486 | error 0.0020 |
| Monte Carlo, 100k paths | 10.4205 ± 0.047 | 0.64 standard errors |

**Convergence.** A *path* is one simulated possible future for the stock, so more paths should mean a more accurate price. To find out how much more, I priced the same option at nine path counts from 100 to 1,000,000.

A single run is prone to errors, since it depends on which random numbers happened to come out, so at each count I ran the pricer 20 times with a different *seed* — the starting value for the random number generator, which fixes the set of random draws — and averaged the error.

That gives nine points of path count against typical error, and the relationship between them is a **power law**: error ≈ C × N^k. The exponent k is what matters, because it says how fast the error shrinks. k = -0.5 means ten times the paths gives only √10 ≈ 3.2 times less.

To find k, take logs of both sides: log(error) = log(C) + k·log(N), a straight line with slope k. So plotting on log-log axes and fitting a line *measures* the exponent instead of assuming it. **The measured slope was -0.52**, against a theoretical -0.5. The small gap is because each of my nine error values is itself only an average of 20 runs, so it carries noise of its own — more runs per point would tighten it.

![Monte Carlo convergence](analysis/convergence.png)

**Accuracy is expensive.** Going from 100 to 1,000,000 paths is 10,000 times the compute, and it cut mean error from 1.226 to 0.0123 — a factor of 100, exactly √10,000. Since the exponent can't be improved, each extra decimal place costs about 100× the compute. That's why *variance reduction*, which shrinks the constant C rather than the exponent, matters more than simply running more paths.

**The binomial tree converges faster**, as 1/N: ten times the steps for an extra digit, where Monte Carlo needs a hundred times the paths. The trade-off is reach, as the tree enumerates a fixed grid of prices the stock is allowed to reach, so it only ever knows *where* the price ended up, never *how it got there* — which rules out payoffs depending on the whole path, like an option on the year's average price.

Full tables in [results.md](results.md).

---

## Validation

10 tests. The rule: a test is only worth writing if it checks against something known
**independently of my implementation**.

- **Put-call parity**, at-the-money and across five strikes. Follows from no-arbitrage
  rather than from any model, so it must hold whatever I wrote. 
- **Monte Carlo within 3 standard errors** of the closed form, with its standard error
  halving when paths quadruple.
- **Binomial converging** to the closed form at N = 2000.
- **Limiting cases**: zero volatility collapses to discounted intrinsic value; deep
  in-the-money approaches a forward.
- **American ≥ European put**, since an extra right can't reduce value — and **American
  call = European call without dividends**, the classic result that early exercise of a
  call is never optimal, verified to 1e-10.

---

## What I got wrong / Understanding 

Initially I thought Monte Carlo was a *more realistic* model catching what Black-Scholes misses. It isn't.

For a standard European option, Black-Scholes calculates the exact theoretical value using a clean, closed-form calculus equation. Monte Carlo merely approximates that same equation by generating thousands of random paths and averaging the outcomes—a process that is slower, computationally heavy, and introduces sampling error.
For example, its like the game of rolling a dice: 
- for a simple option: game of rolling 6 to win $10
  M.C : rolls a die 10,000 times then averages the payoffs (approximate outcome) 
  B.S : uses the exact maths to find expected value at E(x) = 1/6 * $10 (perfect outcome)

In fact, running test_mc_matches_bs proves that for a vanilla option, Monte Carlo is strictly worse; if the simulation captured some hidden "realism," that unit test would fail. 

- but for a more complex option: roll 20 times. Win $10 only if numbers rise three times in a row, but lose everything if you roll a 1.
  M.C : very hard to write up :(
  B.S : A computer simulates this 20-roll sequence 100,000 times. The simulation easily tracks the rules, counts the successes, and averages the payoffs.

True market realism comes entirely from modifying the underlying data assumptions—such as adding stochastic volatility or jump-diffusion processes. Because these complex mathematical models lack a closed-form formula, they require simulation to solve. Monte Carlo does not supply the realism; it is simply the only computational tool flexible enough to survive complex changes to variables (influenced by market conditions).

---

## Limitations

Constant volatility is the load-bearing assumption, and the market openly disagrees: the volatility smile is exactly the market pricing in fat tails this model rules out. Returns are assumed log-normal, trading continuous and costless, and dividends zero in the reported results.

So this is reasonable for liquid, short-dated, near-the-money European options — and poor for long-dated ones, deep out-of-the-money ones, and anything path-dependent.

---

## Running it

    pip install -r requirements.txt
    pytest -v
    python -m analysis.convergence

Reference: Hull, *Options, Futures and Other Derivatives*.
