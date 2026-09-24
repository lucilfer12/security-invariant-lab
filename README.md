# Security Invariant Lab

A lightweight, extensible framework for finding security bugs by turning **security invariants** into executable tests over state transitions.

## Research model

**Invariant → State transition → Reachability → Violation → Minimization → Evidence → Regression**

The goal is not to label every suspicious line as a vulnerability. The lab makes a security claim executable, searches reachable state, minimizes a failing trace, and preserves machine-readable evidence.

## What it is for

- Stateful smart-contract and protocol logic
- Accounting and conservation properties
- Replay protection and nonce monotonicity
- Authorization and lifecycle invariants
- Cryptographic binding properties
- Differential testing between implementations
- Reproducing and regression-testing security findings

## Architecture

```text
                    ┌─────────────────────┐
                    │   System Adapter     │
                    │ model / RPC / EVM /  │
                    │ Rust harness / other │
                    └──────────┬──────────┘
                               │
                     state + transitions
                               │
                    ┌──────────▼──────────┐
                    │     Invariant       │
                    │ executable property │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Explorer/Fuzzer   │
                    │ deterministic paths │
                    └──────────┬──────────┘
                               │ failure
                    ┌──────────▼──────────┐
                    │     Minimizer       │
                    │ shortest bad trace  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │      Evidence       │
                    │ JSON + Markdown     │
                    └─────────────────────┘
```

## Quick start

```bash
python -m unittest discover -s tests -v
python -m examples.defi_payout_shortfall
python -m examples.replay_nonce_reset
python -m examples.pqc_seed_binding
python -m examples.fuzzing
python -m examples.control_cases
```

The examples are intentionally synthetic and local. They do not contact live services or contain operational attack tooling.

## CLI

After installing the package locally:

```bash
silab demo all
silab demo replay
silab run examples/replay_nonce_reset.py
```

## Repository structure

```text
invariant_lab/          Core framework
examples/               Self-contained research models
adapters/               Foundry/Rust integration notes
findings/               Add sanitized case studies here
reports/                Generated evidence (ignored by Git)
tests/                  Regression tests
docs/                   Methodology, threat modeling, fuzzing, and extension guides
templates/              Finding and invariant templates
schemas/                Machine-readable evidence schema
.github/workflows/      Continuous integration
```

## Design principles

1. **Claim before exploit.** Write the security invariant first.
2. **Reachability matters.** A violation must be reachable under explicit capabilities.
3. **State is evidence.** Capture the state before and after the violating transition.
4. **Minimize failures.** Keep the smallest sequence that still violates the invariant.
5. **Separate discovery from impact.** The framework records technical failures; severity is a separate research judgment.
6. **Prefer regression.** Every confirmed invariant violation should become a permanent test.
7. **Keep research sanitized.** Use synthetic identities and data in public examples.

## Scope

This is an educational and research-oriented framework. It is designed for local models, authorized test environments, and reproducible findings. It is not a scanner for live targets and does not provide unauthorized access mechanisms.
