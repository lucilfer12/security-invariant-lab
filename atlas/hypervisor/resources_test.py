from atlas.hypervisor.resources import PageTable, VCPU, VCPUScheduler


def test_vcpu_priority_and_rotation():
    scheduler = VCPUScheduler()
    scheduler.add(VCPU(1, "guest-b", 1))
    scheduler.add(VCPU(0, "guest-a", 2))
    scheduler.add(VCPU(2, "guest-a", 1))
    assert scheduler.next().guest_id == "guest-a"
    assert scheduler.next().guest_id == "guest-a"
    assert scheduler.next().guest_id == "guest-b"
    assert scheduler.remove_guest("guest-a") == 2
    assert scheduler.next().guest_id == "guest-b"


def test_page_translation_and_faults():
    table = PageTable(page_size=4096)
    table.map(3, 11)
    assert table.translate(3 * 4096 + 17) == 11 * 4096 + 17
    assert table.unmap(3) == 11
    try:
        table.translate(3 * 4096)
    except MemoryError as exc:
        assert "page fault" in str(exc)
    else:
        raise AssertionError("unmapped page was translated")


if __name__ == "__main__":
    test_vcpu_priority_and_rotation()
    test_page_translation_and_faults()
    print("ATLAS hypervisor resource tests: PASS")
