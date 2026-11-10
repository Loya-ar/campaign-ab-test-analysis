# Decision memo: email campaign test

**To:** marketing and analytics leads · **Decision needed:** which email (if any) to send

## Recommendation

**Ship the men's-merchandise email as the default campaign.** Don't ship the women's email as a
blanket campaign yet; send it into a targeted follow-up test.

Both emails beat sending nothing, so either one is better than silence. The men's email does
better on every metric. The women's email may work mainly for some customers, but that idea
hasn't yet passed a proper test.

## What we found

64,000 customers were randomly split three ways: men's email, women's email, no email. The
groups were the planned size (sample-ratio test p = 0.90) and alike before the send: on all 11
pre-period features the largest standardized difference was 0.014, and an omnibus test gave
p = 0.89. So the differences below can be put down to the emails.

| Metric (2-week window) | No email | Men's email | Women's email |
|---|---|---|---|
| **Conversion (primary)** | 0.573% | 1.253% | 0.884% |
| Lift vs no email (95% CI) | — | **+0.68 pp** (+0.50 to +0.86) | **+0.31 pp** (+0.15 to +0.47) |
| Holm-adjusted p | — | 3.0e-13 | 1.6e-4 |
| Visit rate | 10.62% | 18.28% (+7.66 pp) | 15.14% (+4.52 pp) |
| Spend per customer | $0.65 | $1.42 (+$0.77, CI +$0.49 to +$1.06) | $1.08 (+$0.42, CI +$0.17 to +$0.68) |
| Spend per buyer (guardrail) | $114.00 | $113.53 (no change) | $121.89 (no change) |

**Both emails pass the decision rule agreed in advance:** a significant conversion lift after
Holm correction, a CI entirely above zero, and no drop in spend per buyer.

**Why men's over women's.** This comparison wasn't in the original plan, so treat it as
supporting evidence rather than proof. The men's email converted 0.37 pp more than the women's
(CI +0.17 to +0.56, p = 0.0002) and brought in $0.35 more per customer (CI +$0.03 to +$0.66,
p = 0.03). In the exploratory segment cuts, the men's email lifted conversion in 21 of 22
segments (raw p < 0.05), the women's email in 11 of 22. The women's email's lift was clearest
among past women's shoppers (+0.51 pp) and new customers (+0.53 pp), and close to zero for
men's-only shoppers (+0.06 pp) and existing customers (+0.09 pp).

## What it's worth

Per 100,000 customers emailed, over two weeks, compared with sending nothing:

| | Men's email | Women's email |
|---|---|---|
| Extra buyers | about 680 (500 to 860) | about 310 (150 to 470) |
| Extra revenue | about $77,000 ($49,000 to $106,000) | about $42,000 ($17,000 to $68,000) |

These are revenue figures, not profit, before the cost of sending. They are in 2008 dollars for
a retailer and cover only the two weeks measured.

## Risks and what we couldn't measure

- **Customer annoyance.** Unsubscribes, spam complaints and opt-outs aren't in the data. A
  bank would make these hard guardrails before rolling out.
- **Spend per buyer is a weak guardrail.** There were only 122 buyers in the no-email group, so
  the CI is about ±$23. We can't rule out a drop of up to about 20% in basket size.
- **Short window.** Two weeks of outcomes say nothing about long-term value or email fatigue
  from repeated sends.
- **Small-effect blind spot.** The test could only reliably detect conversion lifts of about
  43% or more. The observed lifts (119% and 54%) are well above that, but smaller effects on
  other groups or metrics would have been missed.
- **CUPED didn't help here.** Past-year spend barely predicts a 2-week purchase (ρ ≈ 0.03), so
  variance fell by under 0.5%.
- **Segment results are exploratory.** No test of whether lifts differ between segments
  survived multiple-comparison correction (smallest Holm p = 0.10).

## Next steps

1. Roll out the men's email, holding back a random 5–10% of customers who get no email, so the
   lift keeps being measured.
2. Run a follow-up test of the women's email aimed at past women's shoppers and new customers.
   Size it from this test's segment estimates, and fix the sample size before it starts.
3. Track unsubscribes and complaints from the first send.
4. Don't stop tests early by checking p-values as data arrives. Our A/A simulation on real
   customers showed false positives rising from about 5% to 34% with 100 looks. If interim
   looks are needed, use pre-set O'Brien-Fleming boundaries, which kept the rate near 5%.

*Source: Kevin Hillstrom's MineThatData E-Mail Analytics Challenge (2008), a real randomised
test by a US retailer. The method carries over to a bank's marketing campaigns (card offers,
deposit promotions, app nudges); these specific numbers do not.*
