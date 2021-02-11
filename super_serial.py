import selectors
import serial
import threading
import os


class SuperSerial:
    def __init__(self) -> None:
        self.sel = selectors.DefaultSelector()

        self._com = serial.serial_for_url("/tmp/serial1")
        self.sel.register(self._com, selectors.EVENT_READ, self._read)

        self.lines = []
        self.read_lock = threading.Lock()
        self.read_buffer = bytearray()
        self.endline = b"\n"

        self.running = False

    def run(self):
        while self.running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            
    def start(self):
        self.thread = threading.Thread(target=self.run)
        # self.thread.daemon = True
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def _read(self, com, event: int):
        print("COOOM: {}".format(com))
        data = os.read(self._com.fileno(), 1024)
        if data:
            with self.read_lock:
                self.read_buffer.extend(data)
        else:
            print('closing', self._com)
            self.sel.unregister(self._com.fileno())
            self._com.close()

    def write(self, buf: bytes):
        self._com.write(buf)

    def _get_read_buffer(self):
        with self.read_lock:
            buff = self.read_buffer
            self.read_buffer = bytearray()
        return buff

    def read(self) -> bytearray:
        return self._get_read_buffer()

    def readline(self) -> bytearray:
        buff = self._get_read_buffer()
        line, sep, remaining = buff.partition(self.endline)
        with self.read_lock:
            self.read_buffer = bytearray(remaining)
        return line
        

