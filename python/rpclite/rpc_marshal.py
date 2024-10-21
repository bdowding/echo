import struct

def bytes_to_None(data: bytes) -> None:
    return None

def bytes_to_bool(data: bytes) -> bool:
    return struct.unpack(">?", data)[0]

def bytes_to_uint8_t(data: bytes) -> int:
    return struct.unpack(">B", data)[0]

def bytes_to_uint16_t(data: bytes) -> int:
    return struct.unpack(">H", data)[0]

def bytes_to_uint32_t(data: bytes) -> int:
    return struct.unpack(">L", data)[0]

def bytes_to_int8_t(data: bytes) -> int:
    return struct.unpack(">b", data)[0]

def bytes_to_int16_t(data: bytes) -> int:
    return struct.unpack(">h", data)[0]

def bytes_to_int32_t(data: bytes) -> int:
    return struct.unpack(">l", data)[0]

def bytes_to_float(data: bytes) -> float:
    return struct.unpack(">f", data)[0]

def bytes_to_double(data: bytes) -> float:
    return struct.unpack(">d", data)[0]
