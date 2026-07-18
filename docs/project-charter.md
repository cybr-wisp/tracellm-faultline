# Project Charter

## Research question

> Can a corruption-aware agent learn an adaptive verification policy that minimizes expected total cost (token spend + error cost) across heterogeneous failure modes, and how close does this policy come to the oracle-optimal strategy?

## Why this question matters

LLM agents increasingly call external tools in production. When those tools return bad data, the agent can either blindly trust it (cheap but dangerous), or verify it (safe but expensive). The optimal choice depends on the corruption probability, the cost of a wrong answer, and the cost of verification. This is a classic decision-under-uncertainty problem.

We formalize it as a cost-minimization problem with an oracle baseline: if you knew exactly which outputs were corrupted, what would the cheapest correct strategy be? The gap between any real strategy and the oracle is the **price of uncertainty** — a single number that captures how much an agent pays for not knowing whether to trust its tools.

## Key concepts

- **Oracle-optimal strategy:** Computed post-hoc from labeled data. Verifies only when corrupted, using the cheapest effective method. This is the theoretical lower bound on total cost.
- **Regret:** actual_total_cost − oracle_total_cost. Always ≥ 0. Measures how far a strategy is from perfect.
- **Price of uncertainty:** regret / oracle_cost. The fractional overhead of operating without perfect corruption knowledge.
- **Adaptive policy:** Instead of always retrying or always critiquing, the agent inspects signals (output entropy, format validity, consistency with prior steps) to decide per-step whether to verify.

## Intended users

Researchers and engineers evaluating the reliability of tool-using LLM agents, particularly those designing verification strategies for production deployment.

## Hypotheses

1. Static verification strategies (retry, critic, verifier) reduce error rates but at costs that may exceed the value of the errors they prevent, especially when corruption is rare.
2. An adaptive policy that selects verification actions based on corruption signals achieves lower regret than any single static strategy.
3. The price of uncertainty varies by corruption type — plausible-but-wrong outputs are the most expensive to handle because they evade cheap detection methods.

## Non-goals

- Building a production agent framework
- Benchmarking model quality on standard NLP tasks
- Creating a general-purpose prompt playground
- Using any Nokia code, data, or internal material
- Depending on OpenAI's hosted Evals platform (shutting down Nov 2026)
