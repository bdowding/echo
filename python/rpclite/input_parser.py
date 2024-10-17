
import abc
import itertools
from typing import Any, Dict, List, Sequence, Type

import yaml
import hashlib

from rpclite.api_types import ApiEnum, ApiStruct, ApiType, _get_api_type


class ApiRpcParam:
    def __init__(self, contents: Dict, others: Sequence[ApiType]) -> None:
        self.name: str = contents["name"]
        unresolved_type_name = contents["type"]
        self.type = _get_api_type(unresolved_type_name, others)

class ApiRpc:
    def __init__(self, contents: Dict, others: Sequence[ApiType]) -> None:
        self.name = contents["name"]
        self.params = [ApiRpcParam(x, others) for x in contents["params"]]
        self.return_type: ApiType = _get_api_type(contents["return_type"], others)
        self.const: bool = contents["const"]
    
    def invoke(self, parameters: List[Any]) -> Any:
        pass


class ApiDevice:
    def __init__(self, contents: Dict, others: Sequence[ApiType]):
        self.name = contents["name"]
        self.rpcs = [ApiRpc(x, others) for x in contents["rpcs"]]


class InputYaml:
    def __init__(self, filename: str):
        with open(filename, "r") as f:
            text = f.read()
        y = yaml.safe_load(text)
        self._contents = y

        self.enums: List[Dict] = self._contents.get("enums", [])
        self.structs = self._contents.get("structs", [])
        self.devices = self._contents.get("devices", [])
        self.api_name = self._contents.get("api", {}).get("name", "default")


class InputYamlCollection:
    def __init__(self, inputs: List[str]) -> None:
        input_items = [InputYaml(x) for x in inputs]
        self._api_name = input_items[0].api_name

        # Enums can never have dependencies
        unresolved_enums = list(itertools.chain(*[x.enums for x in input_items]))
        self.enums: List[ApiEnum] = [ApiEnum(x) for x in unresolved_enums]

        # Structs can depends on enums or other structs
        unresolved_structs = list(itertools.chain(*[x.structs for x in input_items]))
        self.structs = []
        for x in unresolved_structs:
            self.structs.append(ApiStruct(x, self.enums + self.structs))

        # Rpcs can depends on structs or enums, but not other RPCs
        self.devices = [ApiDevice(x, self.enums + self.structs) for x in itertools.chain(*(x.devices for x in input_items))]

    def get_api_name(self) -> str:
        return self._api_name