from atlas.database.execution import ExecutionEngine


def test_scan_filter_project():
    engine = ExecutionEngine()
    plan = engine.project(
        engine.filter(engine.scan([(1, "a"), (2, "b"), (3, "c")]), 0, ">", 1),
        [1],
    )
    assert engine.run(plan) == [("b",), ("c",)]


def test_hash_join():
    engine = ExecutionEngine()
    left = engine.scan([(1, "alice"), (2, "bob"), (3, "carol")])
    right = engine.scan([(2, "admin"), (3, "user"), (4, "guest")])
    joined = engine.hash_join(left, right, 0, 0)
    assert engine.run(joined) == [(2, "bob", 2, "admin"), (3, "carol", 3, "user")]


def test_predicates():
    engine = ExecutionEngine()
    rows = [(1,), (2,), (3,)]
    assert engine.run(engine.filter(engine.scan(rows), 0, "<=", 2)) == [(1,), (2,)]
    assert engine.run(engine.filter(engine.scan(rows), 0, "!=", 2)) == [(1,), (3,)]


if __name__ == "__main__":
    test_scan_filter_project()
    test_hash_join()
    test_predicates()
    print("ATLAS database execution tests: PASS")
