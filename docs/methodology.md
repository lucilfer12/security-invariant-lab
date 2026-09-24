# Methodology

## 1. State the invariant

Turn a security property into a boolean statement.

Examples:

- `executed_nonce` must be monotonic and never roll back.
- `payout == share_value` before burning a full exit position.
- distinct account contexts must not derive identical key material.
- an authorization capability must be bound to the intended resource.

## 2. Define the state machine

Document the mutable state and the transitions that can change it. Include lifecycle edges: create, rotate, revoke, expire, re-add, upgrade, and recovery.

## 3. Define attacker capabilities

State exactly what the test actor can do. Separate permissionless actions, user actions, privileged actions, and external dependencies.

## 4. Prove reachability

A line that looks dangerous is not enough. The failing state must be constructible under the declared capabilities.

## 5. Execute the invariant

Run it after every relevant transition, not only at the end. This makes the first corrupting edge visible.

## 6. Minimize the trace

Remove irrelevant events while keeping the violation. A five-step minimal trace is often much stronger evidence than a 500-step fuzz trace.

## 7. Capture evidence

Store the invariant name, failing message, pre-state, post-state, trace, seed, model/version, and environment metadata.

## 8. Add the regression

Freeze the minimal counterexample as a test. A fix is not complete until the regression passes and the invariant stays true under the broader test set.
