from pathlib import Path
from tempfile import TemporaryDirectory

from .chaos import ChaosInjector
from .container import Sandbox, SandboxSpec
from .hypervisor import Guest, Hypervisor
from .memory import Permission, VirtualMemory
from .platform import AtlasPlatform

def run() -> None:
    vm = VirtualMemory(16); vm.map(0, 1, Permission.READ | Permission.WRITE)
    vm.write(2, b"atlas"); assert vm.read(2, 5) == b"atlas"
    hv = Hypervisor(); hv.create(Guest("g1", 64, 1)); hv.start("g1"); assert hv.snapshot("g1")["running"]
    box = Sandbox(SandboxSpec("safe", ("echo", "atlas"))); box.start(); assert box.inspect()["read_only"]; box.stop()
    chaos = ChaosInjector(seed=7); assert chaos.fixed("n1", "packet_loss", 0.5).kind == "packet_loss"
    with TemporaryDirectory() as td:
        platform = AtlasPlatform(td); platform.ring.add("n1"); assert platform.health()["models"] == 0
        platform.wal.append("boot", {"ok": True})
        assert Path(td, "cas").exists() and Path(td, "wal.log").exists()

if __name__ == "__main__":
    run(); print("ATLAS subsystem tests: PASS")
