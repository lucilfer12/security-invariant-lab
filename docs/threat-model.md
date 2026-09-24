# Threat Model Worksheet

## Asset

What must not be lost, forged, replayed, or permanently stranded?

## Trusted parties

Which actors are intentionally privileged? Which are merely expected to behave honestly?

## Attacker capabilities

List the exact state transitions available without privilege and with each relevant permission.

## Trust boundaries

Identify contracts, services, signers, relayers, key stores, bridges, or parsers that cross a security boundary.

## Failure modes

Consider:

- replay
- authorization confusion
- stale state
- lifecycle lockout
- accounting drift
- precision loss
- context collision
- differential behavior

## Recovery

Ask whether a bad transition can be reversed. Permanent loss of control deserves separate treatment from an ordinary rejected call.
