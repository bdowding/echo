from __future__ import annotations
import abc
import argparse
import functools
import itertools
from typing import Dict, List, Sequence
import yaml


class NoMatchException(Exception):
    pass

class MultipleMatchException(Exception):
    pass


class ApiType(abc.ABC):
    @abc.abstractmethod
    def get_name(self) -> str: ...


_builtin_types: Dict[str, type] = {
    "uint8_t": int,
    "uint16_t": int,
    "uint32_t": int,
    "uint64_t": int,
    "int8_t": int,
    "int16_t": int,
    "int32_t": int,
    "int64_t": int,
    "float": float,
    "double": float,
    "bool": bool,
    "void": type(None),
}


class ApiEnumEntry:
    def __init__(self, contents: Dict) -> None:
        self.name: str = contents["name"]
        self.value: int = contents["value"]


class ApiEnum(ApiType):
    def __init__(self, contents: Dict):
        self.name: str = contents["name"]
        self.entries = [ApiEnumEntry(x) for x in contents["entries"]]

    def get_name(self) -> str:
        return self.name

class ApiStructField:
    def __init__(self, name: str, api_type: ApiType) -> None:
        self.name: str = name
        self.type: ApiType = api_type


class ApiStruct(ApiType):
    def __init__(self, contents: Dict, others: Sequence[ApiType]):
        self.name = contents["name"]
        self.fields: List[ApiStructField] = []

        for unresolved in contents["fields"]:
            target_type_name: str = unresolved["type"]
            if target_type_name in _builtin_types:
                self.type = _builtin_types[target_type_name]
                continue

            others_matches = [x for x in others if x.get_name() == target_type_name]
            if not others_matches:
                raise NoMatchException(target_type_name)
            elif len(others_matches) > 1:
                raise MultipleMatchException(target_type_name)
            else:
                self.fields.append(ApiStructField(unresolved["name"], others_matches[0]))
            
    def get_name(self) -> str:
        return self.name

class ApiRpcParam:
    def __init__(self, contents: Dict, others: Sequence[ApiType]) -> None:
        self.name: str = contents["name"]
        unresolved_type_name = contents["type"]
        
        if unresolved_type_name in _builtin_types:
            self.type = _builtin_types[unresolved_type_name]
        else:
            others_matches = [x for x in others if x.get_name() == unresolved_type_name]
            if not others_matches:
                raise NoMatchException(unresolved_type_name)
            elif len(others_matches) > 1:
                raise MultipleMatchException(unresolved_type_name)
            else:
                self.type = others_matches[0]

            raise RuntimeError(f"Could not resolve type: {unresolved_type_name}")


class ApiRpc:
    def __init__(self, contents: Dict, others: Sequence[ApiType]) -> None:
        self.name = contents["name"]
        self.params = [ApiRpcParam(x, others) for x in contents["params"]]
        self.return_type: str = contents["return_type"]
        self.const: bool = contents["const"]


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


class InputYamlCollection:
    def __init__(self, inputs: List[str]) -> None:
        input_items = [InputYaml(x) for x in inputs]

        # Enums can never have dependencies
        unresolved_enums = list(itertools.chain(*[x.enums for x in input_items]))
        self.enums: List[ApiEnum] = [ApiEnum(x) for x in unresolved_enums]

        # Structs can depends on enums or other structs
        unresolved_structs = list(itertools.chain(*[x.structs for x in input_items]))
        self.structs = []
        for x in unresolved_structs:
            self.structs.append(ApiStruct(x, self.enums + self.structs))
        
        # Rpcs can depends on structs or enums, but not other RPCs
        self.all_devices = [ApiDevice(x, self.enums + self.structs) for x in itertools.chain(*(x.devices for x in input_items))]
        

def generate_api(inputs: List[str]):
    all_inputs = InputYamlCollection(inputs)
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_folder", action="store")
    parser.add_argument("--input_yamls", action="store", nargs="+")

    args = parser.parse_args()

    generate_api(args.input_yamls)


if __name__ == "__main__":
    main()
