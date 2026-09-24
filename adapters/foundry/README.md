# Foundry adapter plan

A Foundry adapter should:

1. generate a deterministic input sequence;
2. execute it against a local Anvil/fork environment chosen by the researcher;
3. normalize storage/balance/event outputs;
4. feed normalized state to shared invariants;
5. emit a replay bundle containing the test seed and sequence.

The repository does not invoke live chains by default.
