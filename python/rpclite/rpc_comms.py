
import abc
from dataclasses import dataclass
import struct
from typing import Any, Callable, Dict, TypeVar


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


@dataclass
class RpcInfo:
    callback: Callable
    params_code: str
    return_code: str


class RpcServerComms:
    def __init__(self) -> None:
        self._rpcs: Dict[int, RpcInfo] = {}
    
    def on_incoming_message(self, incoming: bytes) -> bytes:
        rpc_index = struct.unpack_from(">H", incoming)[0]
        rpc_info = self._rpcs[rpc_index]
        params = struct.unpack_from(rpc_info.params_code, incoming, 2)
        response_object = rpc_info.callback(*params)

        if response_object is None and rpc_info.return_code == "":
            return b'\0'
        else:
            response_bytes = struct.pack(rpc_info.return_code, response_object)
            return b'\0' + response_bytes

    def register_rpc(self, rpc_index: int, rpc_info: RpcInfo):
        self._rpcs[rpc_index] = rpc_info
