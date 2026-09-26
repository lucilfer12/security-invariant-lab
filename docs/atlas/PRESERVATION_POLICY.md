# ATLAS — Preservation and Change-Control Policy

## Purpose

Prevent accidental destruction while the platform expands from the existing security lab into a multi-domain system.

## Immutable historical baseline

The commit that represents the last known baseline remains reachable forever. New work is additive and branch-based.

## Change classes

- ADD: new capability; preferred default.
- EXTEND: add fields or behavior while preserving old interfaces.
- ADAPT: isolate integration with an adapter.
- MIGRATE: version old data before transformation.
- DEPRECATE: mark old behavior but keep it functional until a replacement is verified.
- REMOVE: forbidden by default; requires an explicit future architecture decision and archival copy.

## Evidence preservation

Every finding keeps its original identifier, source, evidence level, reproduction status, and provenance.

Automated analysis can discover candidates, but cannot silently promote a candidate to verified exploit.

## Test preservation

Existing passing tests remain part of the compatibility suite. New implementations add regression coverage rather than replacing old cases.

## Git discipline

Major domains use dedicated branches. Stable milestones are tagged. Pull requests document scope, compatibility impact, validation, and rollback.

## Failure containment

A new subsystem must be allowed to fail independently. Experimental dependencies cannot silently alter the behavior of the existing security engine.

## Release gate

A milestone is releasable only when tests, static checks, reproducibility checks, documentation, and change provenance are all present.
