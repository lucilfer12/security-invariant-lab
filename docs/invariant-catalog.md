# Invariant Catalog

This catalog is a starting point for hypothesis generation. An entry becomes a useful security test only after the protected asset, state model, and actor capabilities are explicit.

## State and lifecycle

- **Monotonic counter:** a security-relevant nonce or version must never decrease.
- **Single-use capability:** an authorization artifact that was consumed must not become valid again.
- **Lifecycle safety:** revoke/expire/delete/re-add transitions must preserve at least one valid recovery or control path when the protocol promises recoverability.
- **Atomic replacement:** rotation must not expose an intermediate state that is permanently unreachable.

## Accounting

- **Conservation:** assets entering and leaving a system reconcile after fees and explicitly documented rounding.
- **Full-exit correctness:** a full position must not be destroyed unless the promised payout condition is satisfied.
- **Bounded parameter:** caller-supplied economic parameters must stay within protocol-level limits.
- **Precision awareness:** boundary constants must be interpreted in the actual unit and decimal domain used by the contract.

## Authorization

- **Resource binding:** an authorization decision must be scoped to the intended resource, not merely to an action name.
- **Least privilege:** capabilities should cover only the objects and transitions they are intended to control.
- **Revocation effectiveness:** revoked capabilities must cease to authorize future state transitions.

## Cryptography and identity

- **Domain separation:** independent protocol contexts must not share cryptographic domains accidentally.
- **Context binding:** key derivation must include every security-relevant identity/context dimension required by the specification.
- **Key uniqueness:** distinct accounts/roles expected to be independent must not deterministically derive identical secret material.
- **Replay resistance:** previously accepted signed messages must not become acceptable after lifecycle changes.

## Differential properties

- **Implementation agreement:** two conforming implementations should produce equivalent normalized state for the same abstract event sequence.
- **Patch monotonicity:** a security fix should remove the counterexample without introducing a new invariant violation in the same state partition.
