import selectors
import socket

sel = selectors.DefaultSelector()


def _read(conn: socket.socket, _):
    data = conn.recv(1000)  # Should be ready
    if data:
        print('echoing', repr(data), 'to', conn)
        data = data.replace(b"\\n", b"\n")
        conn.send(b"ECHO" + data)  # Hope it won't block
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


def _accept(sock: socket.socket, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, _read)


sock = socket.socket()
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('localhost', 4004))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, _accept)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)