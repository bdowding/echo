
import abc
from dataclasses import dataclass
import struct
from typing import Any, Callable, Dict


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


@dataclass
class RpcInfo:
    callback: Callable[..., Any]
    bytes_to_params: Callable[[bytes], Any]
    return_type_to_bytes: Callable[[Any], bytes]


class RpcServerComms:
    def __init__(self) -> None:
        self._rpcs: Dict[int, RpcInfo] = {}
    
    def on_incoming_message(self, incoming: bytes) -> bytes:
        rpc_index = struct.unpack_from(">H", incoming)[0]
        rpc_info = self._rpcs[rpc_index]
        params = rpc_info.bytes_to_params(incoming[2:])
        response_object = rpc_info.callback(*params)
        response_bytes = rpc_info.return_type_to_bytes(response_object)
        return b'\0' + response_bytes

    def register_rpc(self, rpc_index: int, rpc_info: RpcInfo):
        self._rpcs[rpc_index] = rpc_info
