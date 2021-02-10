import selectors
from socket import socket
import threading


class SuperSerial:
    def __init__(self) -> None:
        self.sel = selectors.DefaultSelector()
        self.sock = socket()
        self.sock.connect(("localhost", 4004))
        self.sock.setblocking(False)
        self.sel.register(self.sock, selectors.EVENT_READ, self._read)

        self.lines = []
        self.read_lock = threading.Lock()
        self.read_buffer = bytearray()
        self.endline = b"\n"

    def run(self):
        while self.running:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
            
    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def _read(self, conn: socket, event: int):
        data = conn.recv(1000)  # Should be ready
        if data:
            with self.read_lock:
                self.read_buffer.extend(data)
        else:
            print('closing', conn)
            self.sel.unregister(conn)
            conn.close()

    def write(self, buf: bytes):
        self.sock.sendall(buf)

    def _get_read_buffer(self):
        with self.read_lock:
            buff = self.read_buffer
            self.read_buffer = bytearray()
        return buff

    def read(self) -> str:
        buff = self._get_read_buffer()
        return buff.decode("UTF-8")

    def readline(self) -> str:
        buff = self._get_read_buffer()
        line, sep, remaining = buff.partition(self.endline)
        with self.read_lock:
            self.read_buffer = bytearray(remaining)
        return line
        

