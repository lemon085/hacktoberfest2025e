#!/usr/bin/env python3
# portbouncer.py - simple honeypot for lab/demo use only
import socket, threading, time

BANNERS = {
    22: b"SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3\r\n",
    80: b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello from PortBouncer\n",
}

LOG = "connections.log"

def handle(conn, addr, port):
    with conn:
        t = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{t} {addr[0]}:{addr[1]} -> local:{port}\n"
        print(line.strip())
        open(LOG,"a").write(line)
        banner = BANNERS.get(port, b"")
        if banner:
            try:
                conn.sendall(banner)
            except:
                pass
        try:
            data = conn.recv(1024)
            if data:
                open(LOG,"a").write(f"DATA {addr[0]}:{addr[1]} {data[:200]!r}\n")
        except:
            pass

def serve(port):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen(5)
    print(f"Listening on {port}")
    while True:
        c, a = s.accept()
        threading.Thread(target=handle, args=(c,a,port), daemon=True).start()

if __name__ == "__main__":
    import sys
    ports = [22,80] if len(sys.argv)==1 else list(map(int,sys.argv[1:]))
    for p in ports:
        threading.Thread(target=serve, args=(p,), daemon=True).start()
    print("PortBouncer running. Ctrl-C to stop.")
    while True:
        time.sleep(3600)
