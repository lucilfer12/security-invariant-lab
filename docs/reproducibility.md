# Reproducibility

A strong reproduction should let another researcher answer four questions:

1. **What claim failed?** Name the invariant precisely.
2. **What state caused the failure?** Capture before/after snapshots.
3. **What exact sequence caused it?** Preserve an ordered event trace.
4. **Can the failure be replayed?** Record model/version information and deterministic seeds.

## Evidence bundle

Use the framework's `build_evidence()` / `write_evidence()` for machine-readable output and `write_markdown()` for a human-readable case report.

## Public release hygiene

Strip production addresses, credentials, seed phrases, private keys, unreleased patch details, confidential bounty communications, and customer data. Prefer synthetic identifiers and toy values.
