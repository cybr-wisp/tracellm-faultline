# Related Work

> **Status:** Complete — Day 2 deliverable

This matrix compares 8 systems and papers relevant to tracellm-faultline's research question:

> Can a corruption-aware agent learn an adaptive verification policy that minimizes expected total cost (token spend + error cost) across heterogeneous failure modes, and how close does this policy come to the oracle-optimal strategy?

---

## Comparison matrix

| System / Paper | Year | What it evaluates | Corruption / fault model | Recovery strategies tested | Cost modeling | Oracle baseline | Key limitation from our perspective |
|---|---|---|---|---|---|---|---|
| **ToolEmu** (Ruan et al.) | 2024 | Risk identification in tool-using LLM agents via LM-emulated sandbox | No controlled corruption; focuses on identifying risky agent behaviors in high-stakes tools | None — measures failures, not recovery | No | No | Identifies that agents fail, but doesn't test whether they can recover or what recovery costs |
| **Inspect AI** (UK AISI) | 2024 | General-purpose LLM evaluation framework (coding, reasoning, agentic tasks) | Sandboxed execution; no systematic fault injection into tool outputs | Built-in ReAct agent; no comparison of recovery strategies | No | No | Excellent engineering, but it's a framework, not a study of recovery under corruption |
| **"Towards a Science of AI Agent Reliability"** (Rabanser et al.) | 2026 | 12 reliability metrics across 4 dimensions (consistency, robustness, predictability, safety) on 14 models | Prompt perturbation and environment variation; not tool-output corruption specifically | None — measures reliability dimensions, not interventions | Resource consistency metric exists, but no cost-optimization framing | No | Defines the right dimensions but doesn't test interventions or frame recovery as a decision problem |
| **Tools Fail** (Sun et al.) | 2024 | LLM ability to detect "silent" tool errors (broken calculator, broken vision models) | Controlled silent errors: perturbed calculator outputs, faulty VLM outputs | Three in-context interventions to improve detection (not full recovery pipelines) | No | No | Focuses on detection as a prerequisite for recovery; doesn't measure end-to-end recovery or its cost |
| **PALADIN** (Vuddanti et al.) | 2026 | Training LLM agents for runtime failure recovery via trajectory-level supervision | Systematic failure injection: timeouts, API exceptions, malformed outputs (50K+ annotated trajectories) | LoRA fine-tuning on recovery trajectories vs. CRITIC, ToolBench Agent, ToolReflect baselines | No | No | Trains agents to recover (changes the model); we evaluate recovery strategies without model modification |
| **CRITIC** (Gou et al.) | 2024 | LLM self-correction via tool-interactive critiquing (search, code interpreter, toxicity classifier) | Not tool-output corruption; uses tools to verify LLM's own outputs | Iterative generate-verify-correct loop using external tools | No | No | Uses tools to fix the agent's outputs, not to handle corrupted tool inputs. No cost analysis of the verification loop |
| **AgentProp-Bench** (Gurram) | 2026 | Judge reliability and error propagation in tool-using agent evaluation | Controlled parameter-level injection; measures propagation probability (~0.62) | Runtime interceptor as mitigation (23pp reduction in hallucination) | No | No | Validates that automated evaluation is unreliable (kappa=0.049 for substring matching); our human review protocol directly addresses this |
| **AgentNoiseBench** | 2026 | Robustness of tool-using agents under noisy user instructions and noisy tool results | Two noise sources: user-side instruction noise and tool-side result noise (failures, partial outputs, erroneous responses) | No recovery strategies — measures degradation under noise | No | No | Measures how much agents break under noise, but doesn't test whether recovery interventions help or what they cost |

---

## What each system contributes to our work

### ToolEmu — Emulated tool environment design
ToolEmu demonstrated that LM-emulated tool execution produces realistic enough failures that 68.8% would be valid in real deployments. We adopt the principle of synthetic tool environments but use deterministic tool simulators rather than LM-emulated ones, giving us ground-truth control over what the "correct" output should have been. This is essential for computing the oracle-optimal strategy.

### Inspect AI — Engineering reference
Inspect AI's architecture (Dataset → Solver → Scorer) influenced our modular design (TaskDefinition → AgentStrategy → Scorer). We use the same provider-agnostic approach (supporting OpenAI, Ollama, and fake providers). However, Inspect is a general evaluation framework. Faultline is a focused research instrument for one specific question about cost-optimal recovery.

### "Towards a Science of AI Agent Reliability" — Metric framework
This paper's decomposition of reliability into consistency, robustness, predictability, and safety directly informs our metric design. We adopt their outcome consistency metric for repeated trials and their resource consistency metric (cost variance across runs). Our contribution is extending this from measurement to optimization: instead of asking "how consistent is the agent?" we ask "what policy minimizes the cost of inconsistency?"

### Tools Fail — Detection as prerequisite
Sun et al. established that LLMs can learn to detect silent tool errors through in-context interventions, but that detection alone is insufficient. Our work starts where theirs ends: given that detection is possible but imperfect, what is the cost-optimal verification policy? Their broken-calculator setting directly inspired our "plausible but incorrect" corruption mode.

### PALADIN — Recovery through training
PALADIN shows that training on recovery-annotated trajectories produces fault-tolerant agents. This is complementary to our approach: PALADIN modifies the agent (fine-tuning), while we evaluate intervention strategies (retry, critic, verifier, adaptive) applied to unmodified models. Our oracle baseline could help PALADIN practitioners decide whether the cost of recovery training is justified for a given corruption base rate.

### CRITIC — Self-verification architecture
CRITIC's generate-verify-correct loop is the direct inspiration for our "critic" and "verifier" agent strategies. However, CRITIC uses tools to verify the agent's own outputs, while we study verification of the tool's outputs to the agent. CRITIC also does not measure the cost of its verification loop — a gap our cost model directly addresses.

### AgentProp-Bench — Evaluation validity
AgentProp-Bench's finding that substring-based evaluation agrees with human annotation at kappa=0.049 (chance-level) is a critical methodological warning. Their three-LLM ensemble judge reaches kappa=0.432 (moderate). We incorporate this by requiring human review of ~50 ambiguous traces and computing inter-rater agreement, rather than relying solely on automated scoring.

### AgentNoiseBench — Noise taxonomy
AgentNoiseBench's distinction between user-side noise and tool-side noise helps scope our work. We focus exclusively on tool-side result noise (their second category) and go deeper: instead of measuring degradation, we test whether specific strategies can mitigate it and at what cost.

---

## The gap our work fills

No existing system combines all of:

1. **Controlled tool-output corruption** (not agent errors, not input noise — corrupted tool results)
2. **Multiple recovery strategies** compared under the same conditions (baseline, retry, critic, verifier, adaptive)
3. **Cost modeling** that assigns dollar values to both token spend and error severity
4. **An oracle-optimal baseline** that establishes the theoretical lower bound on total cost
5. **Regret computation** measuring how far each strategy is from perfect information
6. **Adaptive policy** that decides per-step whether verification is worth the cost

The closest work is a combination of Tools Fail (detection focus) + PALADIN (recovery focus) + Rabanser et al. (reliability metrics), but none of these frames the problem as cost-minimization with oracle bounds. That framing — borrowed from decision theory and optimal stopping — is our primary contribution.

---

## Citation list

1. Ruan, Y. et al. (2024). "Identifying the Risks of LM Agents with an LM-Emulated Sandbox." ICLR 2024. arXiv:2309.15817
2. UK AI Security Institute (2024). "Inspect AI: Framework for Large Language Model Evaluations." https://inspect.aisi.org.uk/
3. Rabanser, S. et al. (2026). "Towards a Science of AI Agent Reliability." ICML 2026. arXiv:2602.16666
4. Sun, J. et al. (2024). "Tools Fail: Detecting Silent Errors in Faulty Tools." EMNLP 2024. arXiv:2406.19228
5. Vuddanti, S. V. et al. (2026). "PALADIN: Self-Correcting Language Model Agents to Cure Tool-Failure Cases." ICLR 2026. arXiv:2509.25238
6. Gou, Z. et al. (2024). "CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing." ICLR 2024. arXiv:2305.11738
7. Gurram, B. (2026). "Evaluating Tool-Using Language Agents: Judge Reliability, Propagation Cascades, and Runtime Mitigation in AgentProp-Bench." arXiv:2604.16706
8. AgentNoiseBench (2026). "Benchmarking Robustness of Tool-Using LLM Agents Under Noisy Condition." ICML 2026. arXiv:2602.11348

### Additional references consulted

- Yao, S. et al. (2024). "τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains." arXiv:2406.12045
- Snell, C. et al. (2025). "Scaling LLM Test-Time Compute Optimally Can be More Effective than Scaling Parameters." ICLR 2025.
- Raman, V. et al. (2025). "Optimal Stopping vs Best-of-N for Inference Time Optimization." arXiv:2510.01394
- Wang, C. et al. (2024). "NoisyToolBench." arXiv reference from robustness benchmarks survey.
