def test_bootloader_and_kernel_scheduler():
    from atlas.machine import Assembler, Bootloader, CPU
    from atlas.os import Kernel, ProcessState
    code = Assembler().assemble("CONST r0, 7\nHALT")
    cpu = CPU()
    cpu.run(code)
    assert cpu.r[0] == 7
    image = Bootloader().build(b"kernel", "1", 0)
    assert Bootloader().load(image).kernel == b"kernel"
    kernel = Kernel()
    kernel.boot()
    p2 = kernel.processes.spawn("worker")
    selected = kernel.tick()
    assert selected is not None
    assert kernel.processes.processes[p2.pid].state in (ProcessState.READY, ProcessState.RUNNING)

def test_http_tls_quic_and_object_storage():
    from tempfile import TemporaryDirectory
    from atlas.network import HTTPRequest, QUICConnection, TLS13Session, parse_request, build_response
    from atlas.storage import ObjectStore, ReedSolomonShard
    req = parse_request(b"GET /health HTTP/1.1\r\nHost: atlas\r\n\r\n")
    assert isinstance(req, HTTPRequest) and req.header("host") == "atlas"
    assert b"Content-Length: 2" in build_response(200, "OK", b"ok")
    tls = TLS13Session()
    tls.client_hello(b"c"); tls.server_hello(b"s")
    assert tls.state.value == "established"
    q = QUICConnection(b"cid", max_data=10)
    assert q.send(b"123") == 1
    q.ack(3)
    with TemporaryDirectory() as td:
        store = ObjectStore(td)
        meta = store.put("docs/a", b"atlas", {"kind": "test"})
        assert store.get("docs/a") == b"atlas"
        assert store.get("docs/a", meta.version) == b"atlas"
    shards = ReedSolomonShard.encode(b"abcdef")
    assert ReedSolomonShard.recover((None, shards[1], shards[2])) == b"abcdef"
def test_validator_admission_and_state_root():
    from atlas.blockchain import SignedTransfer, StateMachine, Transfer, Validator, ValidatorConfig
    state = StateMachine()
    state.fund("a", 50)
    validator = Validator(ValidatorConfig(1), state)
    tx = SignedTransfer(Transfer("a", "b", 10, 0), 21_000, 1, True)
    assert validator.apply_block([tx]) == 1
    assert validator.balance("b") == 10
    assert len(state.state_root()) == 64
    try:
        validator.apply_block([SignedTransfer(Transfer("a", "b", 10, 1), 21_000, 2, True)])
    except Exception as exc:
        assert "chain id" in str(exc)
    else:
        raise AssertionError("wrong chain id must be rejected")
