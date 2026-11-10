# Experiment design

Written as the plan a team would agree on *before* reading the results, with two honest caveats:

- The data was collected in 2008, so the baselines below come from this experiment's own no-email
  group, standing in for the historical rates a team would normally use.
- It was not truly blind: the Step 1 data check printed each group's headline rates before this
  plan was written. The plan sticks to standard choices (conversion primary, two-sided, Holm,
  alpha 0.05) rather than anything tuned to those numbers.

## The experiment

In 2008, 64,000 customers of a US retailer who had bought in the last 12 months were randomly
assigned to three groups. Each group had about 21,300 customers.

| Group | What they got |
|---|---|
| Control | No email |
| Treatment A | An email featuring men's merchandise |
| Treatment B | An email featuring women's merchandise |

Outcomes were tracked for the two weeks after the send.

## Hypotheses

For each treatment vs control (two comparisons):

- **H0:** the treatment's conversion rate equals the control's.
- **H1:** the two rates differ (two-sided test; a harmful email should be caught too).

## Metrics

| Role | Metric | Definition |
|---|---|---|
| **Primary** | Conversion rate | Share of customers who bought in the 2 weeks |
| Secondary | Visit rate | Share of customers who visited the website |
| Secondary | Spend per customer | Dollars spent per customer assigned, buyers and non-buyers (zeros included) |
| Guardrail | Spend per buyer | Average order value among converters; the email shouldn't buy conversions with smaller baskets |
| Guardrail | Sample ratio | The group split should match the planned 1/3 each (SRM check, Step 3) |

Conversion is primary because it is the decision the email is meant to change, and it is less
noisy than spend. Spend per customer is the money metric but is very skewed (median $0, max
$499), so it is secondary and gets a bootstrap as well as Welch's test.

**Guardrails this data can't measure.** A bank running this campaign would also track
unsubscribe rate, spam complaints and opt-outs, because an email that annoys customers costs
future reach. The Hillstrom data has none of these, so the analysis can't check them.

## Decision rule

- Significance level 0.05 family-wise across the two treatments, using **Holm's correction**.
- **Ship** a treatment if its conversion lift is significant after Holm, the confidence interval
  is entirely above zero, and the spend-per-buyer guardrail shows no significant drop.
- Secondary metrics support or qualify the decision but can't by themselves trigger a ship.
- Segment cuts are **exploratory**: they can generate hypotheses for a follow-up test but don't
  change the decision.

## Power analysis

Code: [`src/abtest/power.py`](../src/abtest/power.py). Run: `python scripts/design_power.py`.
Normal approximation, power 0.8. For planning, alpha is 0.025 per comparison: 0.05 split
across two comparisons, the strictest threshold Holm can apply.

Baselines (no-email group): conversion **0.573%**, visit **10.62%**, spend per customer
**$0.653** (SD $11.59).

**Customers needed per group to detect a relative lift in conversion:**

| Relative lift | Treatment rate | n per group (alpha 0.05) | n per group (alpha 0.025) |
|---|---|---|---|
| +10% | 0.630% | 286,121 | 346,494 |
| +20% | 0.687% | 74,914 | 90,722 |
| +30% | 0.744% | 34,798 | 42,141 |
| +50% | 0.859% | 13,608 | 16,480 |
| +100% | 1.145% | 4,076 | 4,936 |

**Minimum detectable effect with the ~21,300 customers per group available:**

| Metric | Baseline | alpha | Absolute MDE | Relative MDE |
|---|---|---|---|---|
| Conversion | 0.573% | 0.025 | 0.248 pp | 43.4% |
| Visit | 10.62% | 0.025 | 0.938 pp | 8.8% |
| Spend per customer | $0.653 | 0.025 | $0.346 | 53.0% |

**What this means.** Conversion is rare (about 6 in 1,000), so even 21,300 customers per group
can only reliably detect a lift of **about 43% or more**. A realistic +10% lift would need
about 350,000 customers per group. Visit rate, being far more common, is much better powered
(an 8.8% relative lift). A non-significant conversion result here would therefore mean "no
large effect", not "no effect". CUPED (Step 5) is one way to get more power out of the same
customers.

Cross-check: for +30% at alpha 0.025 the formula gives 42,141 per group; statsmodels'
arcsine (Cohen's h) method gives 41,962, a 0.4% difference from the different approximation.
