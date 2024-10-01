
import struct
import threading
import time
import serial

class Comms:
    def __init__(self, com_port: str) -> None:
        self._com_port = com_port
        
        self._serial = serial.Serial()
        
    def _blocking_read(self):
        data = self._serial.read()
        data += x if (x := self._serial.read_all()) else bytes()
        return data
        
    def call_function(self, function_index: int, data: bytes):
        try:
            packet = struct.pack("B", function_index) + data
            self._serial.write(packet)
            return self._blocking_read()
        except serial.SerialException:
            self._reconnect()
            return bytes()
    
    def _reconnect(self):
        try:
            self._serial = serial.Serial(self._com_port)
        except serial.SerialException:
            pass