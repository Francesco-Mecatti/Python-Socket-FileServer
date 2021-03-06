import socketserver
import threading
import logging
import argparse

"""
Connect to this server using netcat or similar utilities
"""

HOST, PORT = "127.0.0.1", 9999


# TODO: termina con \n --> adatta ricezione e trasmissione

class RequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        logging.info(f"New connection {self.client_address}".encode())
        while True:
            self.request.sendall(">> ".encode())
            try:
                data = self.request.recv(1024).decode()  # command
            except ConnectionResetError:
                logging.error(f"Closed connection - Reset Connection Error: {self.client_address}")
                break
            if cmd:
                cmd = data[0]
            logging.debug(f"Received: {cmd}")
            if not cmd: break
            if cmd == '0':
                self.request.sendall(f"Client address: {self.client_address}\n".encode())
            elif cmd == '1':
                self.request.sendall(f"Socket address: {self.server.server_address}\n".encode())
            elif cmd == '2':
                self.request.sendall(f"Current thread name: {threading.current_thread().getName()}\n".encode())
            elif cmd == '3':
                self.request.sendall(f"Alive threads number: {threading.active_count()}\n".encode())
            elif cmd == '4':
                self.request.sendall(f"Alive threads: {[t.getName() for t in threading.enumerate()]}\n".encode())
            elif cmd == 'q':
                break
            else:  # Help
                self.request.sendall("""'0': Return the remote address (client) to which the socket is connected;
'1': Return the server socket's own address;
'2': Return the current thread name;
'3': Return the number of alive threads;
'4': Return the list of names of alive threads (comma separated);
'q': Quit server when all the clients will be disconnected;
""".encode())

        self.request.close()
        logging.info(f"Connection closed by client {self.client_address}")


def main(host, port):
    logging.info(f"Server running on {host}:{port}...")

    with socketserver.ThreadingTCPServer((host, port), RequestHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s --> %(asctime)s - %(levelname)s: %(message)s",
                        datefmt="%H:%M:%S")
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", help="host address", default=HOST, type=str, dest="address")
    parser.add_argument("-p", "--port", help="port number", default=PORT, type=int, dest="port")
    args = parser.parse_args()
    PORT = args.port
    HOST = args.address

    try:
        main(HOST, PORT)  # TODO: Keyboard listener
    except KeyboardInterrupt:
        logging.warning("Stopping server...")
