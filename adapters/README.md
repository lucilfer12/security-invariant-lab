# Adapter Notes

The core engine is deliberately language-agnostic.

Adapters should translate an external harness into:

```text
fresh() → state
apply(state, event) → state transition
snapshot(state) → normalized evidence
```

Keep adapter code thin and keep security invariants in the shared test layer.
