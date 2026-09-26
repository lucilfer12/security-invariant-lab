from atlas.crypto import MerkleTree
from atlas.distributed import CausalOrder, compare_vectors
from atlas.network import Action, Firewall, FirewallRule, FirewallPacket, SourceNat


def test_merkle_proof_and_tamper():
    tree = MerkleTree([b"a", b"b", b"c", b"d", b"e"])
    proof = tree.proof(3)
    assert MerkleTree.verify(tree.root, proof)
    assert not MerkleTree.verify(tree.root, type(proof)(3, b"x", proof.siblings))


def test_vector_causality():
    assert compare_vectors({"a": 1}, {"a": 2}) is CausalOrder.BEFORE
    assert compare_vectors({"a": 2}, {"b": 1}) is CausalOrder.CONCURRENT
    assert compare_vectors({"a": 1}, {"a": 1}) is CausalOrder.EQUAL


def test_firewall_and_nat():
    firewall = Firewall([FirewallRule(Action.ALLOW, protocol="tcp", dst_port=443)])
    assert firewall.evaluate(FirewallPacket("10.0.0.2", "8.8.8.8", "tcp", dst_port=443)) is Action.ALLOW
    assert firewall.evaluate(FirewallPacket("10.0.0.2", "8.8.8.8", "udp", dst_port=443)) is Action.DENY
    nat = SourceNat("203.0.113.10")
    first = nat.translate("10.0.0.2", 1234, "TCP")
    second = nat.translate("10.0.0.2", 1234, "TCP")
    assert first == second
    assert first.public_ip == "203.0.113.10"


if __name__ == "__main__":
    test_merkle_proof_and_tamper()
    test_vector_causality()
    test_firewall_and_nat()
    print("ATLAS eleventh-wave tests: PASS")
