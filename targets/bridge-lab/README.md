# Bridge Regression Lab

This target is intentionally local and synthetic. It demonstrates the SIL evidence loop against a real EVM execution environment.

## Demonstrated

- vulnerable message processing with the one-time marker written after an external call;
- fixed message processing with the one-time marker committed before the external call;
- a re-entrant receiver;
- Foundry regression tests executing both implementations.

## Run

Install Foundry and forge-std, then run:

    forge test -vvv

The dependency under lib/forge-std is local tooling and is intentionally ignored by Git.

## Security boundary

Do not point this lab at live targets or real funds. SIL's EVM adapter is intended for projects and environments the researcher is authorized to test.
