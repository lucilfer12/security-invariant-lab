def test_replicated_kv_quorum_and_catchup():
    from atlas.distributed import ReplicatedKV
    kv = ReplicatedKV(["r1", "r2", "r3"])
    assert kv.put("a", b"1") == 1
    kv.set_online("r2", False)
    assert kv.put("b", b"2") == 2
    assert kv.get("b", "r1") == b"2"
    assert kv.get("b", "r2") is None
    kv.set_online("r2", True)
    assert kv.catch_up("r2") == 2
    assert kv.get("b", "r2") == b"2"
    assert kv.shard_for("a", 16) in range(16)

def test_service_mesh_and_histogram():
    from atlas.network import Endpoint, Service, ServiceMesh
    from atlas.observability import HDRHistogram
    mesh = ServiceMesh(seed=3)
    mesh.register(Service("api", [Endpoint("a", "10.0.0.1"), Endpoint("b", "10.0.0.2")]))
    assert mesh.route("api").address in {"10.0.0.1", "10.0.0.2"}
    h = HDRHistogram((1.0, 5.0, 10.0))
    for value in (0.5, 2, 7, 20): h.observe(value)
    assert h.total == 4
    assert h.mean > 0
    assert h.quantile(0.5) in {5.0, 10.0}
