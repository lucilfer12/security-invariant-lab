from .ai.security import AgentSandbox, ToolPolicy
from .blockchain.vm import Op, VM
from .build import BuildManifest, cache_key
from .consensus import Entry, RaftNode
from .identity import IAM, Principal, Role, Delegation
from .database import SQLDatabase, parse_sql
from .network import TCPSession, TCPState
from .observability import Histogram
from .sim import Cluster, Event

def run() -> None:
    iam = IAM(); iam.principals["u"] = Principal("u")
    iam.roles["reader"] = Role("reader", frozenset({"read:x"})); iam.bindings["u"] = {"reader"}
    assert iam.allow("u", "read", "x") and not iam.allow("u", "write", "x")
    assert Delegation("a", "b", frozenset({"read"})).child("c", frozenset({"read"})).depth == 1
    node = RaftNode("n1"); node.become_candidate(); node.become_leader(); node.commit(node.append({"op":"set"}).index); assert node.commit_index == 0
    db = SQLDatabase(); db.create_table("t"); db.execute(parse_sql("INSERT INTO t VALUES ('a')")); assert db.execute(parse_sql("SELECT * FROM t")) == [("a",)]
    session = TCPSession(); session.connect(); session.syn_ack(); assert session.state == TCPState.ESTABLISHED; session.close(); session.ack_close()
    hist = Histogram(); hist.observe(0.1); assert hist.total == 1 and hist.mean() == 0.1
    code=[(Op.PUSH,2),(Op.PUSH,3),(Op.ADD,None),(Op.HALT,None)]; assert VM().run(code) == 5
    manifest=BuildManifest("gcc","1","hash","x",("-O2",)); assert len(cache_key(manifest,{"a":"b"})) == 64
    box=AgentSandbox(ToolPolicy(frozenset({"read"}),2)); box.invoke("read"); assert not box.authorize("write")
    cluster=Cluster(); cluster.add_node("n1"); cluster.schedule(Event(2,"n1","down")); assert cluster.run(3)[0].kind == "down"

if __name__ == "__main__":
    run(); print("ATLAS second-wave tests: PASS")
