from typing import Type, TypeVar


T = TypeVar('T')

def args_to_type(t: Type[T], args) -> T:
    return t.__new__(t, *args)
    