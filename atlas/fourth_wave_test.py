def test_contract_resource_frontend():
    from atlas.contracts.lang import ContractParser
    source = """
    contract Vault
    resource Token { owned balance: u64; }
    fn deposit(user, amount) requires authenticated move Token -> unit;
    """
    module = ContractParser().parse(source)
    assert module.name == "Vault"
    assert module.resources["Token"][0].owned
    assert module.functions["deposit"].moves == ("Token",)

def test_defi_invariants_and_oracle_guard():
    from decimal import Decimal
    from atlas.defi.primitives import ConstantProductPool, MedianOracle, LendingPosition, liquidation_amount
    pool = ConstantProductPool(Decimal("1000"), Decimal("1000"))
    before = pool.invariant()
    assert pool.swap_x_for_y(Decimal("10")) > 0
    assert pool.invariant() > before
    oracle = MedianOracle(500)
    price, safe = oracle.safe([Decimal("100"), Decimal("101"), Decimal("99")])
    assert price == Decimal("100")
    assert safe
    pos = LendingPosition(Decimal("5"), Decimal("600"))
    assert liquidation_amount(pos, Decimal("100"), Decimal("0.8"), Decimal("0.5")) == Decimal("300")

def test_secure_kdf_and_compare():
    from atlas.crypto.secure import derive_key, secure_compare
    salt = b"s" * 16
    key1 = derive_key(b"password", salt, iterations=100_000)
    key2 = derive_key(b"password", salt, iterations=100_000)
    assert secure_compare(key1, key2)
    assert not secure_compare(key1, derive_key(b"other", salt, iterations=100_000))

def test_cloud_scheduler_and_autoscaler():
    from atlas.cloud.scheduler import Autoscaler, Node, Scheduler, Workload
    scheduler = Scheduler([Node("n1", 4, 8), Node("n2", 4, 8)])
    assert len(scheduler.schedule(Workload("api", 2, 4, 2))) == 2
    assert scheduler.nodes["n1"].used_cpu + scheduler.nodes["n2"].used_cpu == 4
    auto = Autoscaler(1, 10)
    assert auto.desired(2, 1.4) == 4

def test_tensor_matmul_quantization_and_kv_cache():
    from atlas.ai.tensor import DynamicBatcher, KVCache, Tensor, quantize_int8
    a = Tensor((1, 2), [1, 2])
    b = Tensor((2, 1), [3, 4])
    assert a.matmul2d(b).values == [11]
    q = quantize_int8([0.0, 1.0, 2.0])
    assert len(q.dequantize()) == 3
    cache = KVCache(2)
    cache.append(a, a)
    cache.append(a, a)
    assert len(cache) == 2
    batch = DynamicBatcher(2)
    for n in range(3):
        batch.submit(n)
    assert batch.pop_batch() == [0, 1]
