
from typing import Dict, List, Sequence, Tuple, Type

from rpclite.exceptions import MultipleMatchException, NoMatchException


_builtin_types: Dict[str, Tuple[type, str]] = {
    "uint8_t": (int, "B"),
    "uint16_t": (int, "H"),
    "uint32_t": (int, "I"),
    "uint64_t": (int, "L"),
    "int8_t": (int, "b"),
    "int16_t": (int, "h"),
    "int32_t": (int, "i"),
    "int64_t": (int, "l"),
    "float": (float, "f"),
    "double": (float, "d"),
    "bool": (bool, "?"),
    "void": (type(None), "")
}


class ApiType:
    def get_name(self, none_type: bool = False) -> str: ...


class ApiPrimitive(ApiType):
    def __init__(self, python_type: Type, struct_code: str) -> None:
        self._python_type = python_type
        self._struct_code = struct_code

    def get_name(self, none_type: bool = False) -> str:
        if self._python_type is type(None):
            if none_type:
                return "type(None)"
            else:
                return "None"
        else:
            return self._python_type.__name__
        
    def get_struct_code(self) -> str:
        return self._struct_code


def _get_api_type(type_name: str, others: Sequence[ApiType]):
    if type_name in _builtin_types:
        return ApiPrimitive(*_builtin_types[type_name])

    others_matches = [x for x in others if x.get_name() == type_name]
    if not others_matches:
        raise NoMatchException(type_name)
    elif len(others_matches) > 1:
        raise MultipleMatchException(type_name)
    else:
        return others_matches[0]


class ApiEnumEntry:
    def __init__(self, contents: Dict) -> None:
        self.name: str = contents["name"]
        self.value: int = contents["value"]


class ApiEnum(ApiType):
    def __init__(self, contents: Dict):
        self.name: str = contents["name"]
        self.entries = [ApiEnumEntry(x) for x in contents["entries"]]

    def get_name(self, none_type: bool = False) -> str:
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
            self.fields.append(ApiStructField(unresolved["name"], _get_api_type(target_type_name, others)))

    def get_name(self, none_type: bool = False) -> str:
        return self.name
