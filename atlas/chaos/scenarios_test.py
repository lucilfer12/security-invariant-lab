from atlas.chaos.scenarios import FailureKind, FailurePlan, FailureSpec


def test_failure_plan_validation():
    plan = FailurePlan()
    plan.add(FailureSpec("node-1", FailureKind.PACKET_LOSS, 0.25, 3))
    plan.add(FailureSpec("node-2", FailureKind.CLOCK_SKEW, 5, 2))
    assert plan.validate()
    assert len(plan.active(0)) == 2
    assert len(plan.active(2)) == 1


def test_failure_rejects_invalid_values():
    try:
        FailureSpec("", FailureKind.NODE_DOWN).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("empty target accepted")
    try:
        FailureSpec("n", FailureKind.LATENCY, -1).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("negative magnitude accepted")


if __name__ == "__main__":
    test_failure_plan_validation()
    test_failure_rejects_invalid_values()
    print("ATLAS chaos scenario tests: PASS")
