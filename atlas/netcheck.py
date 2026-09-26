from .network import Packet, RouteTable, Router
from .network import TCPSession

def run() -> None:
    route = Router(RouteTable({"10.": "edge"}))
    hop, packet = route.forward(Packet("a", "10.1", b"payload"))
    assert hop == "edge" and packet.ttl == 15
    session = TCPSession(); session.connect(); session.syn_ack(); session.close(); session.ack_close()

if __name__ == "__main__":
    run(); print("ATLAS network tests: PASS")
