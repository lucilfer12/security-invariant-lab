# Architecture

The framework separates **what the system means** from **how the system is executed**.

## Core layers

### Model

A model owns mutable state and applies events.

### Invariant

An invariant observes state and returns `InvariantResult`.

### Engine

The engine executes a sequence and checks invariants after each event.

### Explorer / Fuzzer

`SequenceFuzzer` generates deterministic event sequences from a seed.

### Minimizer

`minimize_trace` performs greedy delta debugging to keep the smallest failing sequence.

### Evidence

`build_evidence` and `write_evidence` serialize findings for archiving or CI artifacts.

## Adapter strategy

Keep integrations thin. An adapter should translate an external system into a small `fresh/apply/snapshot` interface rather than duplicate the security logic inside the adapter.

Suggested adapters:

- Foundry: invoke a deterministic test harness and ingest emitted state/traces.
- Rust: expose a small model crate or subprocess harness.
- EVM RPC: use forked/local state only for authorized testing and preserve a snapshot identifier.
- Differential: execute the same abstract event sequence against two implementations and compare normalized states.
