# ATLAS — Master Architecture

ATLAS is the long-horizon evolution of Security Invariant Lab into a unified computing, security, verification, protocol, and developer platform.

This document is the architectural anchor. Existing work remains authoritative unless explicitly superseded by a versioned design decision.

## Non-destructive rules

1. Never delete an existing finding, test, proof, fixture, dataset, or document merely to reorganize it.
2. Prefer additive modules, adapters, migrations, and compatibility layers.
3. Every schema change is versioned.
4. Every automated promotion records provenance.
5. Every risky refactor lands behind a branch and a reversible commit.
6. Generated artifacts never become the sole source of truth.
7. A failing new subsystem must not silently weaken an existing security guarantee.

## System domains

- ATLAS Core: shared types, configuration, provenance, lifecycle, policy, and execution contracts.
- Compute: ISA, emulator, compiler, runtime, kernel, virtualization, and operating-system research.
- Network: packet model, transports, routing, secure channels, service networking, and simulation.
- Data: storage engines, transactions, replication, indexing, object storage, and distributed data systems.
- Cloud: scheduling, isolation, orchestration, resource management, identity, secrets, and operations.
- Security: cryptography, identity, authorization, supply-chain security, detection, forensics, and response.
- Verification: invariants, symbolic execution, model checking, fuzzing, differential testing, and proof artifacts.
- Protocols: blockchain execution, consensus, smart contracts, DeFi, bridges, MEV, and economic security.
- AI: model runtime, serving, agents, sandboxing, provenance, and AI-specific security.
- Developer Platform: CLI, SDKs, package management, build systems, debugging, profiling, and documentation.
- Research: benchmarks, RFCs, experiments, datasets, reproducibility, and publications.

## Dependency law

Lower layers must not import higher-level product policy. Cross-domain communication occurs through stable interfaces and versioned contracts.

The intended dependency direction is:

foundation → compute/network/data → distributed/platform → security/verification → protocol/cloud/AI → applications

Security and verification may observe every layer, but they must not become hidden global state.

## First-class artifacts

ATLAS treats these as durable engineering objects:

- source code
- specifications
- RFCs
- threat models
- invariants
- test vectors
- traces
- evidence bundles
- benchmarks
- findings
- incident records
- reproducibility manifests
- release attestations

## Current foundation

The existing Security Invariant Lab is preserved as the first security/verification nucleus. Its invariant engine, fuzzing, differential testing, evidence handling, Solidity scanner, Foundry adapter, bridge target, reporting, and CLI are retained and expanded rather than replaced.
