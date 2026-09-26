from atlas.compiler import BytecodeCompiler, BytecodeVM, compile_expr


def test_codegen_constants_and_parameters():
    module = compile_expr("calc", ("x",), "x + 2 * 3")
    code = BytecodeCompiler().compile_function(module.functions["calc"])
    assert BytecodeVM().run(code, {"x": 4}) == 10


def test_codegen_rejects_unknown_ir():
    from atlas.compiler import IRFunction
    fn = IRFunction("bad", ())
    fn.emit("unknown")
    try:
        BytecodeCompiler().compile_function(fn)
    except ValueError as exc:
        assert "unsupported IR opcode" in str(exc)
    else:
        raise AssertionError("unknown IR opcode was accepted")


if __name__ == "__main__":
    test_codegen_constants_and_parameters()
    test_codegen_rejects_unknown_ir()
    print("ATLAS compiler codegen tests: PASS")
