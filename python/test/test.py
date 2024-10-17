import rpclite
import output.test_api_client
import output.test_api_server
import rpclite.rpc_comms

rpclite.generate("test_input.yaml", "output")

class DirectClient(rpclite.rpc_comms.ClientTransportLayer):
    def __init__(self, server: rpclite.rpc_comms.RpcServerComms) -> None:
        super().__init__()
        self._server = server
        
    def request(self, outgoing_bytes: bytes) -> bytes:
        return self._server.on_incoming_message(outgoing_bytes)


def main():
    down_queue = []
    up_queue = []
    server = rpclite.rpc_comms.RpcServerComms()
    client_comms = DirectClient(server)
    e = output.test_api_server.EchoSensorDevice(server)
    e.setPowerEnabled(True)


if __name__ == "__main__":
    main()