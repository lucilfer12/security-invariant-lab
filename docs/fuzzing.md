# Fuzzing Strategy

The bundled fuzzer is deliberately deterministic and dependency-free.

## Seed discipline

Every generated case records the seed in case metadata. Reproduction therefore requires the same model version, seed, and configuration.

## Sequence generation

Generate actions from an explicit event grammar. Avoid random byte noise unless the security property is byte-level.

Good grammars model domain transitions:

```text
create → authorize → execute → revoke → re-add → execute
```

rather than unconstrained method calls.

## Shrinking

First shrink the sequence, then shrink event parameters. Keep the invariant as the oracle.

## Coverage mindset

Track lifecycle edges and state partitions, not just line coverage. Important partitions include:

- zero / one / many
- before / at / after expiry
- exact boundary / one unit below / one unit above
- fresh / rotated / revoked / re-added
- empty / partially funded / fully funded
