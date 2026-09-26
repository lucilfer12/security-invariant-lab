# Platform Roadmap

The roadmap is organized by capability layers rather than deleting and replacing earlier releases.

## Foundation — completed

- deterministic stateful engine
- invariant API
- sequence fuzzer
- trace minimizer
- evidence serialization
- self-contained research models
- differential execution
- event coverage

## Security Intelligence — completed in platform layer

- Solidity source inventory
- contract/function/state extraction
- heuristic security pattern detection
- attack surface graph
- call and state-reference graph
- candidate invariant discovery
- basic taint-path hypotheses
- security coverage report
- threat model generation
- mutation candidates
- replay bundle metadata
- HTML and Markdown report generation
- local dashboard server
- detector registry and plugin SDK

## EVM execution — adapter-ready

- Foundry build/test adapter
- local bridge regression target
- vulnerable/fixed contract pair
- deterministic regression test
- explicit no-live-target default## Verification expansion

- state-guided corpus evolution
- coverage-guided scheduling
- parameter shrinking
- persistent corpus federation
- semantic differential testing
- temporal properties
- protocol state machines
- symbolic execution adapter
- SMT solver interface
- proof/counterexample status model

## Protocol intelligence

- DeFi accounting pack
- oracle safety pack
- bridge/message pack
- upgradeability/storage pack
- authorization/role pack
- cryptographic binding pack
- ERC property packs
- cross-version and patched/unpatched comparison

## Developer platform

- GitHub PR checks
- SARIF/JUnit output
- CI policy gates
- VS Code integration
- project workspace
- interactive state explorer
- transaction/call visualizer
- findings deduplication
- root-cause graph
- blast-radius analysis

## AI and research

- Gemini evidence-aware analyst
- automatic invariant hypotheses
- attack-sequence hypotheses
- regression-test generation
- research dataset export
- benchmark harness
- experiment coordinator
- distributed workers
- reproducibility manifests
