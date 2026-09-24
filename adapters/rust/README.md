# Rust adapter plan

For Rust protocols, expose a narrow harness that maps abstract events to native test calls and emits a serializable state snapshot. Keep the Rust implementation responsible for execution; keep invariant definitions in the research layer when practical.
