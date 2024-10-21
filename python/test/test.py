
import rpclite
import rpclite.rpc_comms

rpclite.generate("test_input.yaml", "output")

import output

class DirectClient(rpclite.rpc_comms.ClientTransportLayer):
    def __init__(self, server: rpclite.rpc_comms.RpcServerComms) -> None:
        super().__init__()
        self._server = server
        
    def request(self, outgoing_bytes: bytes) -> bytes:
        return self._server.on_incoming_message(outgoing_bytes)


class DummyEchoSensorDevice(output.server.EchoSensorDevice):
    def __init__(self, comms: rpclite.rpc_comms.RpcServerComms):
        super().__init__(comms)
        self._power = False

    def isPowerEnabled(self) -> bool:
        return self._power

    def setPowerEnabled(self, power: bool) -> None:
        self._power = power

    def getStatus(self) -> output.api_types.EchoSensorStatus:
        return output.api_types.EchoSensorStatus(
            output.api_types.PowerState.PoweredOff,
            1.234, 
            output.api_types.WidgetInfo(1.1, 2)
        )



def main():
    server_comms = rpclite.rpc_comms.RpcServerComms()

    client_transport = DirectClient(server_comms)
    client_comms = rpclite.rpc_comms.RpcClientComms(client_transport)

    client_api = output.client.EchoSensor(client_comms)
    device = DummyEchoSensorDevice(server_comms)
    
    power = client_api.isPowerEnabled()
    print(f"Power: {power}")
    client_api.setPowerEnabled(True)
    power = client_api.isPowerEnabled()
    print(f"Power: {power}")
    status = client_api.getStatus()
    print(status)


if __name__ == "__main__":
    main()