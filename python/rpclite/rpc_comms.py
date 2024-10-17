
import abc
import struct
from typing import Callable, TypeVar


T = TypeVar("T")


class ClientTransportLayer(abc.ABC):
    @abc.abstractmethod
    def request(self, outgoing_bytes: bytes) -> bytes:
        pass


class RpcClientComms:
    def __init__(self, transport_layer: ClientTransportLayer) -> None:
        self._transport_layer: ClientTransportLayer = transport_layer

    def invoke_rpc(self, rpc_index: int, parameters: bytes) -> bytes:
        request_bytes = struct.pack(">H", rpc_index) + parameters
        response = self._transport_layer.request(request_bytes)

        # TODO check status
        status = response[0]

        response_payload = response[1:]
        return response_payload


class RpcServerComms:
    def __init__(self) -> None:
        self._rpcs = {}
    
    def on_incoming_message(self, incoming: bytes) -> bytes:
        rpc_index = incoming[0]
        self._rpcs[rpc_index](incoming[1:])

    def register_rpc(self, rpc_index: int, rpc_callback: Callable):
        self._rpcs[rpc_index] = rpc_callback
