# Faultline V1.0 — Project Foundation

## A Cost-Sensitive Reliability Evaluation Framework for Tool-Using AI Agents

Faultline evaluates when verifying an LLM agent's tool outputs prevents enough downstream error to justify its computational cost.

---

## 1. Research Specifications

### 1.1 Research Question

What are the break-even conditions under which tool-output verification becomes cost-negative for LLM agents, how do these conditions vary across output conditions, and how closely can a signal-based adaptive policy track the oracle-optimal verification frontier?

### 1.2 Why This Question Matters

LLM agents increasingly call external tools in production. When those tools return bad data, the agent faces a decision: blindly trust the output (cheap but dangerous) or verify it (safe but expensive). The existing literature overwhelmingly assumes verification is beneficial and asks how to do it efficiently. We ask the prior question: when does verification destroy value?

Verification has two failure modes that the literature treats unevenly. False negatives (missing corruption) are well-studied. False positives (verifying clean outputs and wasting tokens, or worse, flipping a correct answer to an incorrect one) are not. When corruption is rare, most verification spend is wasted on clean outputs. When corruption is plausible-but-wrong, even expensive verification may fail to detect it. The optimal policy depends on three interacting variables: the corruption rate, the output condition, and the downstream cost of a wrong answer.

We formalize this as a cost-minimization problem. The oracle-optimal verification frontier is the surface in (corruption rate × error cost × output condition) space that defines the cheapest correct strategy at every point. Any real strategy's distance from this frontier is its regret. The ratio of regret to oracle cost is the price of uncertainty — how much an agent pays for not knowing whether to trust its tools. We measure where each static strategy (retry, critic, verifier) crosses from cost-positive to cost-negative, and how closely a signal-based adaptive heuristic tracks the oracle frontier across the full parameter space.

### 1.3 Objectives and Contributions

No existing paper combines all four of the following elements. This intersection is Faultline's contribution:

1. Controlled corruption injection with a typed taxonomy (clean, explicit error, malformed, plausible-but-wrong), enabling output-condition-specific analysis rather than aggregate failure rates.

2. Comparison of multiple recovery strategies (baseline, retry, critic, verifier, adaptive heuristic) on the same tasks under the same conditions, producing strategy-level crossover analysis rather than single-strategy evaluation.

3. Oracle-optimal baseline computing the cheapest correct strategy from post-hoc labeled data, enabling regret and price-of-uncertainty measurement rather than accuracy-only reporting.

4. Cost-parameterized analysis sweeping error cost across two orders of magnitude (100–5,000 token equivalents), producing break-even frontiers and crossover charts rather than fixed-cost conclusions.

### 1.4 Hypotheses

H1 — Verification has a break-even frontier, not a break-even point.

Each static verification strategy (retry, critic, verifier) becomes cost-negative below a corruption-rate threshold that depends on both the error cost and the output condition. This threshold is lowest for plausible-but-wrong (verification stays cost-positive longer because detection is harder) and highest for explicit errors (verification becomes cost-negative earliest because cheap detection suffices). The frontier is a surface, not a line.

H2 — An adaptive policy tracks the oracle frontier more closely than any static strategy.

A signal-scoring heuristic that selects verification intensity per tool call based on observable corruption signals achieves lower regret relative to the oracle-optimal strategy than any single static strategy applied uniformly, across all corruption rates and error costs tested.

H3 — The price of uncertainty is output-condition-dependent and asymmetric.

Plausible-but-wrong outputs carry the highest price of uncertainty across all three cost dimensions: detection cost (they evade cheap structural checks), recovery cost (they require the most expensive verification tier), and damage-when-missed cost (they produce confidently wrong final answers that score as full failures). The gap between any real strategy and the oracle is widest for this output condition.

---

## 2. Key Concepts

### 2.1 Concept Summary

| Concept | Definition |
|---|---|
| Oracle-optimal verification frontier | Computed post-hoc from labeled data. Defines the cheapest correct strategy across corruption rate, error cost, and output condition. |
| Break-even threshold | The corruption rate below which a strategy costs more than the damage it prevents. |
| Regret | Actual total cost minus oracle total cost. |
| Price of uncertainty | Regret divided by oracle cost. |
| Cost-negative verification | Verification costs more than using Baseline. |
| Adaptive policy | A signal-based routing policy that selects Pass, Retry, Critic, or Verifier. |

Note on terminology: We use "output condition" instead of "corruption type" when referring to the full set of four conditions (clean, explicit error, malformed, plausible-but-wrong), because clean is one of the four conditions but is not corruption.

### 2.2 Formal Notation

| Symbol | Meaning |
|---|---|
| S | Agent strategy |
| p | Corruption rate |
| C_e | Downstream error cost |
| k | Output condition |
| x | Observable signal vector |
| S* | Oracle-optimal strategy |
| π(x) | Adaptive routing policy |

### 2.3 Actual Total Cost

C_total(S) = C_tokens(S) + E[Damage_missed] + E[Damage_flipped]

The complete economic cost of running strategy S, composed of three terms:

- C_tokens(S): The total token spend across all LLM calls in the trajectory, including the base task call, all verification calls (critic, verifier), all retry calls, and the final answer generation. This is the execution and verification cost.

- E[Damage_missed]: The expected downstream damage from undetected corruption. Computed as (1 − detection rate) × C_e. When the agent fails to detect corrupted tool output and produces a wrong final answer, the downstream cost is C_e. This term captures the cost of false negatives.

- E[Damage_flipped]: The expected downstream damage from verification-induced answer flips. Computed as (answer flip rate) × C_e. When the agent verifies a clean output and incorrectly changes a correct answer to a wrong one, the downstream cost is C_e. This term captures the hidden cost of false positives — the cost of verification making things worse.

The three-part decomposition is what distinguishes this framework from prior work. Most existing cost models include only C_tokens and E[Damage_missed]. The E[Damage_flipped] term formalizes the observation from SeVRA and the Self-Verification Dilemma that verification can destroy value on clean outputs.

### 2.4 Baseline-Relative Verification Value

V(S) = C_total(Baseline) − C_total(S)

This metric directly answers whether a verification strategy creates or destroys value relative to doing nothing:

- V(S) > 0: Verification is cost-positive. Strategy S is cheaper in total than Baseline. Verification creates value.
- V(S) = 0: Break-even. Strategy S costs exactly as much as Baseline in total.
- V(S) < 0: Verification is cost-negative. Strategy S is more expensive in total than Baseline. Verification destroys value. The cure costs more than the disease.

V(S) does not reference the oracle. It answers a simpler question than regret: not "how close to optimal?" but "better or worse than doing nothing?" Both metrics are needed. V(S) identifies cost-negative regimes. Regret measures how much room for improvement remains even in cost-positive regimes.

### 2.5 Oracle-Optimal Frontier

S*(p, C_e, k) = argmin_S C_total(S | p, C_e, k)

Computed post-hoc with full ground-truth knowledge. Defines the minimal-cost verification policy across the parameter space of corruption rate (p), downstream error cost (C_e), and output condition (k).

Properties of the oracle:

- It is computed post-hoc from labeled data. It is not an agent run during execution.
- It uses ground-truth labels to know exactly which tool outputs are corrupted and which are clean.
- For each tool call, it selects the cheapest verification action that would have produced a correct final answer.
- For clean outputs, the oracle selects Pass (no verification). Cost: zero verification overhead.
- For corrupted outputs, the oracle selects the cheapest tier (Retry, Critic, or Verifier) that successfully corrects the corruption in that specific case.
- It is a theoretical lower-cost reference. No real strategy can achieve lower total cost because no real strategy has access to ground truth at inference time.
- It is a surface, not a point. It returns a different optimal strategy at different (p, C_e, k) coordinates, which is what produces the crossover charts.

### 2.6 Break-Even Threshold

p*(S, k, C_e)

The critical corruption rate for a given (S, k, C_e) triple at which:

C_total(S) = C_total(Baseline)

Equivalently, the point at which V(S) = 0.

Below p*, verification is cost-negative: ΔC_tokens + E[Damage_flipped] > ΔE[Damage_prevented]. The additional token spend and answer-flip damage from verification exceed the damage that verification prevents.

Above p*, verification is cost-positive: ΔE[Damage_prevented] > ΔC_tokens + E[Damage_flipped]. Verification prevents more damage than it costs.

Each strategy × output condition × error cost triple has its own break-even threshold. The collection of all p* values across the parameter space forms the break-even frontier — a surface, not a line.

### 2.7 Regret

R(S) = C_total(S) − C_total(S*) ≥ 0

The absolute economic penalty incurred by strategy S due to operating with imperfect information relative to the post-hoc oracle. Always non-negative. Zero only when the strategy matches the oracle's decision at every tool call.

Regret captures a different dimension than V(S). A strategy can be cost-positive (V(S) > 0, better than Baseline) while still having high regret (far from the oracle). Regret measures how much room for improvement remains even among strategies that beat Baseline.

### 2.8 Price of Uncertainty

PoU(S) = R(S) / C_total(S*)

The scale-invariant, normalized overhead paid for lack of perfect corruption foresight. Enables direct comparison across different task lengths, model sizes, and token pricing models.

Interpretation: A PoU of 0.3 means the strategy costs 30% more than the oracle-optimal policy. A PoU of 0 means the strategy matches the oracle exactly. A PoU of 1.0 means the strategy costs double the oracle.

Edge case: When C_total(S*) = 0 (e.g., all outputs are clean and the oracle pays only base execution cost with zero verification overhead), PoU is undefined. In practice, C_total(S*) is always positive because base execution tokens are always spent. If edge cases arise, report R(S) directly instead of PoU.

### 2.9 Cost-Negative Verification

C_total(S) > C_total(Baseline)

Equivalently: R(S) > R(Baseline)

Equivalently: V(S) < 0

A strategy is cost-negative when the sum of verification token spend and induced answer flips exceeds the expected harm of undetected tool errors. Doing nothing (Baseline) would have been cheaper in total. The cure costs more than the disease.

Cost-negative verification can arise from two mechanisms:

1. Over-verification of clean outputs: When corruption is rare, most verification spend is wasted on outputs that were already correct. The token cost accumulates without preventing any damage.

2. Answer flips on clean outputs: Verification sometimes causes the agent to change a correct answer to an incorrect one. This is pure damage created by the verification process itself, with no offsetting benefit.

Both mechanisms are captured in the C_total decomposition. E[Damage_flipped] covers answer flips. The C_tokens term covers over-verification waste.

### 2.10 Adaptive Policy Formalization

π(x) → {Pass, Retry, Critic, Verifier}

A lightweight, inference-time gating function that evaluates an observable signal vector x as a low-cost proxy for P(Corrupted | x) to escalate verification intensity only when economically justified.

The signal vector x contains 3–5 observable features:

- Parsability: Does the output parse as valid structured data? (Binary)
- Length anomaly: Is the output length within expected bounds? (Continuous)
- Semantic drift: Does the output content align with the task context? (LLM-scored, 0–1)
- Format match: Does the output schema match the expected tool response format? (Binary)
- Prior error history: How many tool failures have occurred earlier in this run? (Count)

The oracle knows P(Corrupted | x) = {0, 1} with certainty — it has ground truth. The adaptive policy estimates this probability from observable signals. The price of uncertainty is the cost of that estimation being imperfect.

Implementation details (signal formulas, weights, thresholds, and routing logic) are specified separately in the Adaptive Policy Specification document. This section defines what π(x) means mathematically. The specification document defines how it is implemented.

---

## 3. Locked V1 Scope

- 12 synthetic tasks across 3 domains (order support, scheduling, structured data analysis)
- 4 output conditions (clean, explicit error, malformed, plausible-but-wrong)
- 5 agent strategies (baseline, retry, critic, verifier, adaptive-heuristic)
- 2 core model sources (GPT-4o API, Llama 3.1 8B via Ollama)
- 5 repeated trials per configuration
- Oracle frontier computed post-hoc from labeled data
- Error cost swept across 5 values: 100, 500, 1,000, 2,500, 5,000 token equivalents
- ~2,400 core trajectories
- Human review: ~50 ambiguous or representative traces
- All data is synthetic — no proprietary or employer-sourced material

### Primary Outputs

- Break-even thresholds p* for each strategy × output condition × error cost triple
- Verification value V(S) for each strategy at each point in the parameter space
- Regret R(S) for each strategy at each point in the parameter space
- Price of uncertainty PoU(S) per strategy, with output-condition breakdown
- Crossover charts showing where each strategy transitions from cost-positive to cost-negative
- Oracle-optimal verification frontier surface

---

## 4. Intended Users

- Researchers evaluating reliability of tool-using LLM agents
- Engineers designing cost-sensitive verification strategies for production agent deployment
- Anyone preparing to discuss agent reliability and decision-under-uncertainty in technical interviews

---

## 5. Non-Goals (V1)

- Production agent framework — Faultline is an evaluation tool, not a deployment system
- General-purpose benchmark suite — we study one specific question about verification economics, not broad agent capability
- Learned adaptive policy — V1 uses handcrafted heuristic signals; a trained classifier/bandit is V2
- Nokia proprietary material — zero Nokia code, data, prompts, APIs, documentation, customer information, or internal examples
- OpenAI Evals platform dependency — the engine must remain provider-independent (OpenAI Evals becomes read-only October 2026, shuts down November 2026)
- Authentication, billing, user accounts — the dashboard is a research tool, not a product
- More than 2 core model providers — depth over breadth; stretch pair (Claude Sonnet 4.6 + Qwen 2.5 7B) is V2
- General-purpose prompt playground — the interface serves the research question, not open-ended experimentation

---

## 6. Success Criteria at Day 50

### The project is successful if:

1. The experiment runs end-to-end — 2,400 trajectories complete with full tracing and stored results
2. The oracle frontier is computable — post-hoc cost floor calculated from labeled data at every (p, C_e, k) coordinate
3. Break-even thresholds are identified — for each strategy × output condition pair
4. Verification value V(S) is reported — showing which strategies create and destroy value at each parameter point
5. The crossover chart exists — showing where each strategy transitions from cost-positive to cost-negative as error cost varies
6. PoU is reported per output condition — demonstrating asymmetry across conditions
7. H1 is testable — we can identify the corruption rate below which each static strategy becomes cost-negative
8. H3 is testable — plausible-but-wrong is quantifiably compared to other output conditions on all three cost dimensions
9. The project installs from a clean clone — git clone → docker compose up → working system
10. A reviewer can inspect any trajectory — from the dashboard or exported traces
11. The research report is written — 8–12 pages, methods through discussion, with limitations
12. No confidential material is present — zero Nokia or employer-specific content

### The project is impressive if:

- The adaptive heuristic demonstrably closes the gap to the oracle across the full parameter space
- The crossover chart reveals a non-obvious strategy boundary (e.g., verifier becomes cost-negative before critic at high error costs)
- The price of uncertainty for plausible-but-wrong is measurably and significantly higher than other output conditions
- The break-even frontier is a surface with interesting topology, not a flat plane
- V(S) reveals regimes where every static strategy is cost-negative but the adaptive policy is cost-positive
- The dashboard tells the story without requiring explanation

---

## 7. V2 Roadmap (Out of Scope for V1)

- Learned adaptive policy — train a classifier or contextual bandit on V1 trajectory data to select verification strategy per tool call, directly optimizing for PoU minimization
- Stretch model pair — Claude Sonnet 4.6 + Qwen 2.5 7B for cross-family generalizability
- Domain-weighted error costs — assign task-domain-specific penalties instead of uniform sweep
- Additional model providers — broader open-weight and commercial model coverage
- Multi-step task chains — tasks requiring 3+ sequential tool calls with cascading corruption
- Real tool integration — replace synthetic tools with live API calls to test natural failure modes
- Corruption rate estimation — extend the adaptive policy to estimate p online from observed signals, closing the loop on the decision-theoretic framework

---

## 8. Milestone Timeline

| Deadline | Required Outcome |
|---|---|
| Day 4 | Research question, hypotheses, and experiment plan frozen |
| Day 12 | CLI evaluation engine saving complete runs |
| Day 19 | Functional traced prototype (v0.1.0) |
| Day 27 | Defensible metrics and annotation workflow (v0.2.0) |
| Day 34 | Frozen experiment results and initial findings (v0.3.0) |
| Day 40 | Interview-ready dashboard and repository (v0.4.0) |
| Day 45 | Reproducible release candidate (v1.0.0-rc1) |
| Day 50 | Public V1 — report, dataset, demo, and launch (v1.0.0) |

---

Document version: 4.0
Created: 2026-08-01
Last updated: 2026-08-04