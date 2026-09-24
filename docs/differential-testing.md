# Differential Testing

Differential testing asks whether two implementations that should agree actually do.

Normalize outputs before comparison:

```python
normalized_a = adapter_a.normalize(output_a)
normalized_b = adapter_b.normalize(output_b)
assert normalized_a == normalized_b
```

Use this for:

- reference model vs production implementation
- old version vs patched version
- two language implementations
- specification-derived model vs implementation

A mismatch is evidence for investigation, not an automatic security severity classification.
