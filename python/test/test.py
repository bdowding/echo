import output.test_api_types
import rpclite
import rpclite.rpc_comms

rpclite.generate("test_input.yaml", "output")

import output.test_api_client
import output.test_api_server


class DirectClient(rpclite.rpc_comms.ClientTransportLayer):
    def __init__(self, server: rpclite.rpc_comms.RpcServerComms) -> None:
        super().__init__()
        self._server = server
        
    def request(self, outgoing_bytes: bytes) -> bytes:
        return self._server.on_incoming_message(outgoing_bytes)


class DummyEchoSensorDevice(output.test_api_server.EchoSensorDevice):
    def __init__(self, comms: rpclite.rpc_comms.RpcServerComms):
        super().__init__(comms)
        self._power = False

    def isPowerEnabled(self) -> bool:
        return self._power

    def setPowerEnabled(self, power: bool) -> None:
        self._power = power

    def getStatus(self) -> output.test_api_client.EchoSensorStatus:
        return output.test_api_client.EchoSensorStatus(
            output.test_api_types.PowerState.PoweredOff,
            1.234
        )



def main():
    server_comms = rpclite.rpc_comms.RpcServerComms()

    client_transport = DirectClient(server_comms)
    client_comms = rpclite.rpc_comms.RpcClientComms(client_transport)

    client_api = output.test_api_client.EchoSensor(client_comms)
    device = DummyEchoSensorDevice(server_comms)
    
    power = client_api.isPowerEnabled()
    print(f"Power: {power}")
    client_api.setPowerEnabled(True)
    power = client_api.isPowerEnabled()
    print(f"Power: {power}")


if __name__ == "__main__":
    main()