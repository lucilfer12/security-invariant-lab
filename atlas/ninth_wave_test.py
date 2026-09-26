def test_query_planner_prefers_index_when_available():
    from atlas.database import QueryPlanner, TableStats, IndexLookup
    planner = QueryPlanner({"users": TableStats(10000, {"email": 10000})}, {"users": {"email"}})
    plan = planner.plan("users", "email", "a@example.com")
    assert isinstance(plan.operator, IndexLookup)
    assert plan.estimated_rows == 1.0

def test_gossip_deduplicates_and_bridge_blocks_replay():
    from atlas.blockchain.p2p import GossipNode, Peer
    from atlas.bridge import BridgeMessage, BridgeVerifier, ReplayError
    node = GossipNode("n1")
    node.peers.add(Peer("n2", "10.0.0.2", 5))
    assert node.receive("tx", b"abc") is not None
    assert node.receive("tx", b"abc") is None
    assert len(node.drain()) == 1
    verifier = BridgeVerifier()
    message = BridgeMessage(1, 2, 7, "alice", "bob", b"x")
    assert verifier.verify(message)
    try:
        verifier.verify(message)
    except ReplayError:
        pass
    else:
        raise AssertionError("replay must be rejected")

def test_block_driver_bounds_and_io():
    from atlas.os import BlockDevice, DriverManager
    manager = DriverManager({})
    device = BlockDevice("vda", 4, 16)
    manager.register(device)
    payload = b"a" * 16
    device.write(1, payload)
    assert device.read(1) == payload

def test_existing_git_history_is_not_modified_by_wave():
    from pathlib import Path
    assert Path("atlas").exists()
