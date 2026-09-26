from atlas.compiler import BytecodeVM, Instruction, TypeChecker, INT, BOOL
from atlas.crypto import combine_secret, split_secret
from atlas.database import BTreeIndex


def test_compiler_layers():
    checker = TypeChecker()
    assert checker.check_binary("+", INT, INT) == INT
    assert checker.check_binary("==", BOOL, BOOL) == BOOL
    code = [Instruction("PUSH", 4), Instruction("PUSH", 5), Instruction("ADD"), Instruction("HALT")]
    assert BytecodeVM().run(code) == 9


def test_index():
    idx = BTreeIndex()
    idx.put(3, "c")
    idx.put(1, "a")
    idx.put(2, "b")
    assert idx.range(1, 3) == [(1, "a"), (2, "b")]
    idx.delete(2)
    assert idx.get(2) is None


def test_threshold_secret():
    secret = b"atlas-secret"
    shares = split_secret(secret, 5, 3)
    assert combine_secret(shares[:3]) == secret
    assert combine_secret([shares[0], shares[2], shares[4]]) == secret


if __name__ == "__main__":
    test_compiler_layers()
    test_index()
    test_threshold_secret()
    print("ATLAS fifteenth-wave tests: PASS")
