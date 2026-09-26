# Security Invariant Lab

Security Invariant Lab (SIL) is an executable security research platform for stateful systems.

Core research loop:

Security claim → state transition → reachability → violation → minimization → evidence → reproduction → regression

The original deterministic invariant engine and research examples remain intact. The platform layer adds source intelligence, attack-surface mapping, candidate property discovery, graph analysis, taint hypotheses, mutation candidates, AI-assisted reasoning, report generation, and an authorized EVM adapter.

## What exists now

- Deterministic stateful execution and seeded fuzzing
- Differential execution and normalized state comparison
- Failure minimization and evidence serialization
- Solidity source inventory with contract/function/state extraction
- Security-pattern heuristics with explicit evidence and confidence
- Attack-surface and call/data-flow graphs
- Candidate security-property discovery
- Replayable evidence bundles with Git commit and environment metadata
- Security coverage, threat-model, and taint reports
- Mutation candidate generation without overwriting source
- Built-in detector registry and plugin SDK
- Local HTML/Markdown reports and a dashboard server
- Gemini AI copilot through the GEMINI_API_KEY environment variable
- Foundry adapter for authorized local forge test / forge build
- A local bridge lab containing vulnerable/fixed Solidity plus regression tests

## Quick start

Run the original regression suite, then scan the local bridge lab. The generated .silab directory contains machine-readable evidence and reports.## Architecture

SECURITY INVARIANT LAB

Source intelligence
→ contract inventory
→ control/data-flow hypotheses
→ attack surface

Execution
→ deterministic models
→ stateful fuzzing
→ differential testing
→ minimization

Verification
→ executable invariants
→ candidate properties
→ reachability hooks
→ optional symbolic/SMT backends

Evidence
→ findings
→ replay bundle
→ graph
→ report
→ regression artifact

AI
→ hypothesis generation
→ root-cause discussion
→ test suggestions
→ evidence-linked explanation

The platform is evidence-first. Heuristic findings are hypotheses until a deterministic execution artifact, property check, or external verifier confirms them.## Repository map

invariant_lab/core
  Original execution, invariants, fuzzing, minimization.

invariant_lab/platform
  Security intelligence platform layer.

invariant_lab/platform/detectors
  Extensible detector registry.

adapters/evm
  Executable Foundry adapter.

targets/bridge-lab
  Local vulnerable/fixed EVM regression lab.

schemas
  Machine-readable contracts.

docs
  Methodology and architecture.

examples
  Original local research models.

tests
  Regression suite.

## AI

Set GEMINI_API_KEY in the shell environment. Set GEMINI_MODEL to override the model. The default is gemini-3.8-flash. The AI layer produces hypotheses and analysis text; it is never treated as proof.## Security model

SIL is designed for local models and explicitly authorized test environments. It does not select live targets, bypass access controls, or ship unauthorized exploitation mechanisms. Network-facing adapters must be configured by the researcher.

## Evidence model

Every platform run can emit:

- run metadata
- source and Git revision
- seed and configuration
- candidate properties
- attack graph
- taint paths
- finding fingerprints
- reproduction bundle
- Markdown and HTML report

The intended end state is a platform where a security claim can move from a human hypothesis to an executable property and then to a reproducible research artifact.

## Design doctrine

Claim first. Make reachability explicit. Preserve state. Minimize the smallest failing trace. Separate detection from impact analysis. Never present heuristic output as proof. Prefer regression artifacts over prose-only findings.## Expansion architecture

The codebase is structured for additional capabilities without replacing the original engine:

- multiple language adapters
- richer AST, CFG and DFG analysis
- state-guided and coverage-guided distributed fuzzing
- symbolic execution and SMT backends
- temporal property checking and protocol state machines
- DeFi, oracle, bridge, upgradeability and cryptographic property packs
- GitHub, CI and IDE integrations
- corpus federation, benchmarks and research datasets
- root-cause and blast-radius analysis
- optional cloud workers and plugin marketplace

These are extension points. The repository does not claim a capability merely because a placeholder interface exists.

## ATLAS universal-platform layer

ATLAS is the additive systems layer above SIL. It now has executable reference components for a 64-bit ISA/emulator, deterministic scheduling, virtual memory, policy/capability security, packet routing, cryptographic primitives, distributed clocks and consistent hashing, MVCC storage, CAS/WAL persistence, protocol messages, hypervisor and container reference models, blockchain state/merkle primitives, AI model registry and batching, chaos injection, observability, and a unified composition root.

```bash
python -m atlas.tests
python -m atlas.subsystems_test
python -m atlas.cli self-test
python -m atlas.cli manifest
```

Gemini remains an optional copilot and reads credentials only from the environment. Secrets are excluded by `.gitignore` and are never persisted in source.

## License

See LICENSE.
