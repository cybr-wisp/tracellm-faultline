# Faultline V1 — Related Work

---

## Research Question

What are the break-even conditions under which tool-output verification becomes cost-negative for LLM agents, how do these conditions vary across output conditions, and how closely can a signal-based adaptive policy track the oracle-optimal verification frontier?

---

## Gap Statement

Existing work establishes several components of cost-sensitive reliability evaluation but studies them largely in isolation. ToolMaze and "Don't Blindly Trust It" introduce controlled unreliable tool feedback, while ToolMaze additionally demonstrates that implicit semantic failures are harder to recover from than explicit failures. Sherlock, SeVRA, "When to Trust the Cheap Check," and the Self-Verification Dilemma show that selective verification can reduce unnecessary computation relative to universal checking. CostBench studies economic rationality in tool planning, while Sherlock and theoretically optimal weak-strong policies provide partial precedents for oracle-relative evaluation.

However, existing work does not jointly analyze typed tool-output corruption, multiple verification tiers, downstream error cost, harmful answer flips, and oracle-relative regret. Faultline addresses this gap by estimating a verification break-even frontier over corruption rate, downstream error cost, and output condition, and by measuring how closely a signal-based adaptive policy approaches the resulting oracle-optimal frontier.

No existing work simultaneously:

1. Studies verification break-even conditions on tool outputs (rather than reasoning outputs)
2. Conditions the break-even analysis on output condition (showing the frontier shifts for plausible-but-wrong vs. explicit error)
3. Computes an oracle-optimal verification frontier across a parameterized error-cost sweep
4. Measures how closely a signal-based adaptive policy tracks that frontier

The "when is verification worth it" question has been asked for reasoning. It has not been asked for tool-output corruption, where the answer is more nuanced because output conditions create fundamentally different detection-cost and damage-cost profiles.

---

## Comparison Matrices

### Full Matrix (Internal Documentation)

Legend: ● = directly addressed · ◐ = partially or indirectly addressed · — = not addressed

| Work | Primary Setting | Controlled Tool-Output Corruption | Output-Condition Conditioning | Multiple Verification Strategies | Adaptive Verification Routing | Explicit Cost Model / Harmful Flips | Oracle Comparator | Break-Even Analysis |
|---|---|---|---|---|---|---|---|---|
| Sherlock (Ro et al., 2025) | Multi-node agentic workflows | — | — | ◐ | ● | ● | ● | — |
| When to Trust the Cheap Check (Kiyani et al., 2026) | Weak vs. strong verification of reasoning | — | — | ● | ● | ● | ◐ | ◐ |
| Don't Blindly Trust It (Zhang et al., 2026) | Unreliable feedback in tool-using agents | ● | ◐ | ◐ | — | — | — | — |
| SeVRA (Dip et al., 2026) | Selective verification of reasoning answers | — | — | ● | ● | ● | — | ◐ |
| Self-Verification Dilemma (Long et al., 2026) | Suppression of unnecessary reasoning rechecks | — | — | ◐ | ● | ● | — | ◐ |
| ToolMaze (Zhu et al., 2026) | Tool-failure recovery and dynamic replanning | ● | ● | — | — | — | — | — |
| CostBench (Liu et al., 2025/2026) | Cost-optimal tool planning under dynamic events | ◐ | ◐ | — | ◐ | ● | ◐ | — |
| When Does Verification Pay Off? (Lu et al., 2025) | Solver-verifier relationships across reasoning | — | ◐ | ● | — | ◐ | — | ◐ |
| **Faultline V1 (Proposed)** | **Cost-sensitive verification of corrupted tool outputs** | **●** | **●** | **●** | **●** | **●** | **●** | **●** |

### Condensed Matrix (For Paper)

| Work | Tool Corruption | Typed Failures | Adaptive Selection | Verification Cost | Oracle Comparison | Break-Even Frontier |
|---|---|---|---|---|---|---|
| Sherlock | — | — | ● | ● | ● | — |
| When to Trust the Cheap Check | — | — | ● | ● | ◐ | ◐ |
| Don't Blindly Trust It | ● | ◐ | — | — | — | — |
| SeVRA | — | — | ● | ● | — | ◐ |
| Self-Verification Dilemma | — | — | ● | ● | — | ◐ |
| ToolMaze | ● | ● | — | — | — | — |
| CostBench | ◐ | ◐ | ◐ | ● | ◐ | — |
| When Does Verification Pay Off? | — | ◐ | — | ◐ | — | ◐ |
| **Faultline V1** | **●** | **●** | **●** | **●** | **●** | **●** |

---

## Column Interpretations

### Controlled tool-output corruption

Whether a study deliberately modifies the outputs returned by tools while preserving experimental control. ToolMaze injects explicit/implicit and transient/permanent tool perturbations. "Don't Blindly Trust It" varies returned observations across faithful, misleading, and absent-feedback conditions while holding the surrounding agent loop fixed. CostBench includes dynamic blocking events such as tool failures and cost changes, but its primary focus is planning rather than semantic corruption of tool outputs. The remaining works primarily study naturally occurring reasoning or workflow errors rather than controlled tool-output corruption.

### Output-condition conditioning

Whether results are analyzed separately according to the kind of output condition encountered. ToolMaze directly conditions results on a typed failure taxonomy and reports substantially sharper degradation under implicit semantic failures. "Don't Blindly Trust It" distinguishes faithful, misleading, and absent observations, but does not use Faultline's full explicit-error/malformed/plausible-but-wrong taxonomy. "When Does Verification Pay Off?" shows that verification benefit varies across task categories, but this is task-type conditioning rather than output-condition conditioning.

### Multiple verification or recovery strategies

Whether several intervention mechanisms are evaluated within a shared experimental framework. "When to Trust the Cheap Check" compares weak-only, strong-only, and hybrid weak-strong verification policies. SeVRA compares selective verification with always-verify, longer initial reasoning, and other allocation strategies. "When Does Verification Pay Off?" compares self-, intra-family, and cross-family verification. Sherlock compares verifier choices, but not fundamentally different recovery actions such as Pass, Retry, Critic, and Verifier. Faultline differs by evaluating five strategy types within a single framework.

### Adaptive verification routing

Whether a mechanism selects verification behavior separately for each example, output, or workflow node. Sherlock selectively chooses which workflow nodes deserve verification and which verifier should be attached. "When to Trust the Cheap Check" derives policies that use weak-verification evidence to decide whether strong verification is required. SeVRA trains a recoverability-aware gate that decides whether to preserve the original answer or invoke verification. Self-Verification Dilemma uses past verification experience to suppress rechecks predicted to be unnecessary. Faultline differs by routing among four intervention intensities rather than making only a binary verify/do-not-verify decision.

### Explicit cost model and harmful flips

Whether the study measures verification expenditure or damage introduced by verification itself. Sherlock explicitly optimizes verification cost and latency. "When to Trust the Cheap Check" models strong-verification frequency together with incorrect acceptance and rejection. SeVRA directly reports both token expenditure and harmful answer flips. Self-Verification Dilemma focuses on suppressing largely confirmatory rechecks and reports token reductions while maintaining accuracy. CostBench models tool and planning costs, but not the economic cost of verifying corrupted tool outputs. Faultline's three-part cost decomposition — C_tokens + E[Damage_missed] + E[Damage_flipped] — is unique in explicitly modeling answer flips as an economic cost of verification.

### Oracle or optimal-policy comparator

Sherlock uses cost-aware verifier selection and compares its choices with high-performing verifier alternatives, making it the closest existing analogue to Faultline's oracle-relative evaluation. "When to Trust the Cheap Check" derives an optimal two-threshold policy theoretically, although it does not construct Faultline's post-hoc per-output oracle. CostBench has known cost-optimal tool plans, providing an implicit optimality reference for planning rather than verification. Faultline's proposed oracle is distinct because it uses ground-truth corruption labels to choose the cheapest successful intervention for each tool output.

### Verification break-even analysis

This is the most important differentiator. Several works demonstrate that verification may be wasteful or harmful: SeVRA finds workloads where always-on verification hurts accuracy. Self-Verification Dilemma shows that 85–95% of self-verification steps are confirmatory rather than corrective. "When Does Verification Pay Off?" finds that verification gains vary substantially with solver-verifier similarity and task structure. "When to Trust the Cheap Check" derives threshold policies governing escalation from weak to strong verification.

However, none of these works produces a tool-output verification frontier jointly parameterized by corruption rate × downstream error cost × output condition. That is the central space Faultline is designed to occupy.

---

## Primary Papers (8)

### 1. Sherlock (Microsoft, Nov 2025)

Reference: arXiv 2511.00330

What it does: A framework for reliable and efficient execution of agentic workflows. Uses counterfactual analysis to identify error-prone workflow nodes, selects the most appropriate verifier for each node, and applies speculative execution to minimize latency. Compares its verifier selector against an oracle verifier defined as the one achieving the highest accuracy gain at the lowest cost.

Relationship to Faultline: Sherlock is the closest existing system to our approach. It shares the oracle comparison methodology and cost-aware verifier selection. However, it operates at the workflow-graph level (which nodes to verify) rather than the individual tool-call level (which tool outputs to verify). It selects between different verifier models rather than comparing verification strategy types. Most critically, it does not study output conditions or identify break-even conditions. Faultline's contribution is the output-condition-conditional break-even frontier, which Sherlock's framework does not address.

What we adopt: The oracle comparison methodology and cost-aware framing.

What we extend: From workflow-level to tool-call-level analysis, with typed output conditions and break-even thresholds.

---

### 2. "When to Trust the Cheap Check" (UPenn, ICML 2026)

Reference: arXiv 2602.17633

What it does: Formalizes the tension between weak verification (cheap but noisy) and strong verification (expensive but reliable). Proves that optimal policies admit a two-threshold structure. Develops an online algorithm that controls acceptance and rejection errors without assumptions on the query stream.

Relationship to Faultline: This paper asks the closest theoretical question to ours: when should you use a cheap check versus an expensive check? Their two-threshold structure is conceptually analogous to our escalation policy (Pass → Retry → Critic → Verifier). The key difference is domain: they study reasoning outputs with generic weak/strong verification. We study tool outputs with typed output conditions that create condition-specific break-even surfaces. Their theory does not account for heterogeneous failure modes where the optimal threshold shifts depending on what kind of error occurred.

What we adopt: The cost-aware threshold framework for verification escalation.

What we extend: From homogeneous weak/strong verification to four-level escalation conditioned on output condition.

---

### 3. "Don't Blindly Trust It" (June 2026)

Reference: arXiv 2606.21409

What it does: Introduces a controlled matched-loop comparison to measure whether tool use still outperforms a no-tool fallback under unreliable feedback. Key finding: even a verifier rejecting nearly all corrupted observations with no false accepts yields only limited downstream gains, suggesting that detector quality is not the only bottleneck.

Relationship to Faultline: This paper provides direct empirical motivation for H1 (verification can fail to help even when the verifier is accurate) and H3 (plausible-but-wrong is the hardest output condition). Their finding that a near-perfect verifier still yields limited downstream gains strongly supports our thesis that the economic break-even depends on output condition, not just detection accuracy. We extend their observation from a binary finding ("verification helps less than expected") to a quantitative framework (exactly when does it stop helping, and how does that vary by output condition?).

What we adopt: The empirical evidence that verifier quality alone does not guarantee cost-effective verification.

What we extend: From binary observation to parameterized break-even frontier.

---

### 4. SeVRA / "Think Again or Think Longer?" (Virginia Tech, June 2026)

Reference: arXiv 2606.19808

What it does: A serving-layer controller that decides whether to preserve a frozen solver's initial answer or invoke active verification. Reduces post-generation tokens by 26.8% while reducing harmful answer flips from 2.2% to 1.0%. Key finding: on CommonsenseQA, always-on verification hurts accuracy, demonstrating that the best inference-scaling action is workload-dependent.

Relationship to Faultline: SeVRA is the closest existing work to our adaptive policy concept. Their recoverability-aware gate is a binary classifier (verify or don't), while our adaptive policy is a four-level escalation (Pass → Retry → Critic → Verifier). Their explicit measurement of harmful answer flips validates our inclusion of E[Damage_flipped] in the total cost decomposition. Their finding that verification hurts on CommonsenseQA is exactly the phenomenon we seek to formalize: cost-negative verification. We provide the framework to predict when this happens rather than observing it post-hoc.

What we adopt: The E[Damage_flipped] concept and the evidence that verification can destroy value.

What we extend: From binary gate to four-level escalation, from observation to prediction.

---

### 5. "Self-Verification Dilemma" (Feb 2026)

Reference: arXiv 2602.03485

What it does: Large-scale empirical analysis finding that 85–95% of self-verification steps in large reasoning models are confirmatory rather than corrective. Proposes an experience-driven framework that suppresses overused verification, reducing token usage by up to 20.3% while maintaining accuracy.

Relationship to Faultline: This paper provides the strongest empirical evidence for H1: that universal verification is overwhelmingly wasteful when most outputs are correct. Their 85–95% confirmatory rate directly supports our claim that verification becomes cost-negative below a corruption-rate threshold. The difference is that they observe this empirically for internal reasoning verification. We formalize it for external tool-output verification with a typed output condition taxonomy and oracle baseline.

What we adopt: The empirical evidence that most verification is wasted under low-corruption conditions.

What we extend: From empirical observation to formal break-even framework with parameterized thresholds.

---

### 6. ToolMaze / "When Tools Fail" (June 2026)

Reference: arXiv 2606.05806

What it does: Introduces a benchmark with a 2×2 taxonomy of tool perturbations: explicit/implicit crossed with transient/permanent. Finds that implicit semantic failures cause the sharpest performance drops (~37% recovery rate decline). Also finds that agentic fault-tolerance improves with model scale 3.66× slower than basic task execution.

Relationship to Faultline: ToolMaze's corruption taxonomy (explicit/implicit, transient/permanent) is closely related to ours (explicit error, malformed, plausible-but-wrong). Their finding that implicit semantic failures cause the sharpest drops directly supports H3 (plausible-but-wrong is the most expensive output condition). We extend their finding from a benchmark observation (implicit failures are harder) to a cost-theoretic result (implicit failures have a different break-even threshold and the highest price of uncertainty).

What we adopt: The typed corruption taxonomy and the empirical evidence for corruption-type asymmetry.

What we extend: From recovery-rate benchmarking to cost-theoretic break-even analysis.

---

### 7. CostBench (ACL 2026)

Reference: arXiv 2511.02734

What it does: A cost-centric benchmark evaluating agents' ability to find cost-optimal tool sequences in the travel-planning domain. Supports dynamic blocking events including tool failures and cost changes. Finds that agents frequently fail to identify cost-optimal solutions even in static settings.

Relationship to Faultline: CostBench shares our focus on cost-awareness in tool-using agents, but asks a fundamentally different question. CostBench tests whether agents can find cost-optimal tool sequences (planning). Faultline tests whether agents should verify tool outputs at all (verification economics). CostBench's finding that agents are poor at cost-optimal planning motivates our question: if agents cannot naturally reason about tool costs, can an external framework measure when verification costs exceed their benefits?

What we adopt: The cost-centric evaluation philosophy.

What we extend: From planning cost optimization to verification cost optimization.

---

### 8. "When Does Verification Pay Off?" (NYU, Dec 2025)

Reference: arXiv 2512.02304

What it does: Systematic study across 37 models on 9 benchmarks examining LLM solver-verifier interactions. Finds that cross-family verification is more effective than self-verification and that post-training reduces self-improvement potential. Key finding: not all tasks benefit equally from verification — tasks with verifiable structure yield higher gains than tasks requiring factual recall.

Relationship to Faultline: The title asks our question, but for reasoning verification across model families. Their finding that verification benefit varies by task type supports our claim that verification benefit varies by output condition. We extend this from a qualitative observation ("some tasks benefit more") to a quantitative framework with break-even thresholds, oracle baselines, and cost-parameterized crossover charts.

What we adopt: The question framing — "when does verification pay off?"

What we extend: From qualitative task-type variation to quantitative output-condition-dependent break-even analysis.

---

## Supporting References (13)

### Methodological Validation

DiffAdapt (Oct 2025, arXiv 2510.19669): Oracle per-question strategy selection achieves 50% token savings while improving accuracy by over 10%. Validates our oracle-vs-adaptive methodology for reasoning strategies.

STOCKTAKE (July 2026, arXiv 2607.13618): Fair oracle using an exact Bayes filter on the same observation stream the agent receives. Validates "gap to oracle" as a methodology for agent evaluation.

"Scores Are Not Decisions" (July 2026, arXiv 2607.27083): Cost-aware stopping for tool acquisition under heterogeneous costs. Proves that score-only rules are suboptimal when costs are heterogeneous — supports our claim that output-condition-agnostic policies are suboptimal.

### Corruption and Recovery Benchmarks

ToolMisuseBench (April 2026, arXiv 2604.01508): Offline deterministic benchmark for tool misuse with 6,800 tasks and replayable fault injection. Shares our engineering approach (deterministic, replayable) but measures agent misuse (bad tool calls) not tool corruption (bad tool returns).

AgentNoiseBench (ICML 2026, arXiv 2602.11348): Robustness of tool-using agents under noisy user instructions and noisy tool results. Measures degradation under noise but does not test recovery interventions or their cost. Their tool-side noise category scopes our focus.

PALADIN (ICLR 2026, arXiv 2509.25238): Training LLM agents for runtime failure recovery via trajectory-level supervision with 50K+ annotated trajectories. Complementary approach: PALADIN modifies the agent (fine-tuning), while we evaluate intervention strategies applied to unmodified models. Our oracle baseline could help PALADIN practitioners decide whether the cost of recovery training is justified.

Fission-GRPO (ACL 2026, arXiv 2601.15625): Converts execution errors into corrective RL supervision. V2 relevance — a potential method for training the learned adaptive policy on V1 trajectory data.

### Strategy and Architecture Ancestors

Reflexion (NeurIPS 2023, arXiv 2303.11366): Verbal self-reflection as a recovery mechanism across episodes. Conceptual ancestor of our Critic strategy.

CRITIC (ICLR 2024, arXiv 2305.11738): Tool-interactive critiquing framework. Direct inspiration for our Critic/Verifier strategy distinction. Uses tools to verify the agent's own outputs; we verify the tool's outputs to the agent. Does not measure the cost of its verification loop.

ToolEmu (ICLR 2024, arXiv 2309.15817): LM-emulated tool sandbox for scalable safety testing. We adopt the synthetic tool environment principle but use deterministic simulators for ground-truth control. Essential for computing the oracle-optimal strategy.

### Decision-Theoretic Framing

Calibrate-Then-Act (Feb 2026, arXiv 2602.16699): Formalizes tasks as sequential decision-making under uncertainty with cost-uncertainty tradeoffs. Shares our cost-theoretic framing but for exploration decisions, not verification decisions.

"Cognitive Friction" (April 2026, arXiv 2603.30031): Decision-theoretic framework for bounded deliberation in tool-using agents. Shares our decision-theoretic framing for information acquisition rather than output verification.

"When To Solve, When To Verify" (April 2025, arXiv 2504.01005): Formalizes the compute-allocation tradeoff between generating more solutions versus verifying existing ones. Relevant framing but for reasoning, not tool outputs.

### Additional Context

"Towards a Science of AI Agent Reliability" (Feb 2026, arXiv 2602.16666): Twelve metrics across four reliability dimensions (consistency, robustness, predictability, safety). Our theoretical backbone for reliability measurement. We extend from measurement to optimization.

"Reason Less, Verify More" (July 2026, arXiv 2607.07405): Deterministic pre-execution gates for silent policy violations. Relevant as lightweight, cheap verification analogous to our Retry tier.

"Delayed Verification Destabilizes Multi-Agent LLM Belief" (June 2026, arXiv 2606.27409): Verification that is too strong or too delayed can turn consensus into oscillation. Different setting (multi-agent) but same claim: verification can make things worse.

AgentProp-Bench (April 2026, arXiv 2604.16706): Judge reliability and error propagation with kappa=0.049 for substring matching. Methodological warning that directly motivates our human review protocol and inter-rater agreement requirement.

---

## Summary: Where Faultline Sits

| Dimension | Existing Coverage | Faultline's Contribution |
|---|---|---|
| Corruption injection with typed taxonomy | ToolMaze, ToolMisuseBench, "Don't Blindly Trust It" | Yes — 4 output conditions with distinct cost profiles |
| Comparison of multiple verification strategies | Sherlock, SeVRA, "When to Trust the Cheap Check" | Yes — 5 strategies including adaptive heuristic |
| Cost modeling with economic break-even | CostBench (planning costs), SeVRA (token reduction) | Yes — full cost decomposition C_tokens + E[Damage_missed] + E[Damage_flipped] |
| Oracle baseline with optimality gap | Sherlock (per-node), DiffAdapt (per-question) | Yes — oracle frontier across (p, C_e, k) parameter space |
| Output-condition-conditional analysis | ToolMaze (implicit harder than explicit) | Yes — break-even thresholds vary by output condition |
| Parameterized error-cost sweep | None | Yes — crossover charts across two orders of magnitude |

---

Document version: 2.0
Created: 2026-08-01
Last updated: 2026-08-04