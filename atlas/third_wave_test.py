from .cloud import CloudController, Quota, Resource
from .compiler import compile_expr
from .formal import bounded_check
from .os import FileSystem, ProcessTable
from .packages import Package, Registry

def run() -> None:
    ir = compile_expr("f", ("x",), "2 + 3"); assert ir.optimize() == 1
    fs = FileSystem(); fs.mkdir("/etc"); fs.write("/etc/a", b"x"); assert fs.read("/etc/a") == b"x"
    table = ProcessTable(); proc = table.spawn("init"); table.exit(proc.pid, 0); assert not table.runnable()
    cloud = CloudController(Quota(4, 1024, 100)); cloud.create(Resource("vm1","vm",2,512,10)); assert cloud.usage() == (2,512,10)
    registry = Registry(); pkg = registry.publish(Package("p","1"), b"content"); assert registry.verify(pkg, b"content")
    bad = bounded_check(0, (lambda x: x + 1,), lambda x: x < 3, depth=4); assert bad is not None and bad.depth == 3

if __name__ == "__main__":
    run(); print("ATLAS third-wave tests: PASS")
