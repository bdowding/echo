
import abc

class RpcComms(abc.ABC):
    @abc.abstractmethod
    def invoke_rpc(self, device_name, rpc_name) -> bytes:
        pass