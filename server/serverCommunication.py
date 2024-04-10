import socket
import threading
import queue
import sys
from include.defines import NetworkEvents
import time


class ServerThread:
    def __init__(self, host='activateMotor.local', port=12345, app=None, dummy_server=False):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sockets = []
        self.outgoing_message_queue = queue.Queue()
        self.app = app
        self.dummy_server = dummy_server

    def start(self):
        if self.dummy_server:
            return
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        sys.stdout.flush()
        # Start the message sender thread
        sender_thread = threading.Thread(target=self.message_sender)
        sender_thread.start()

        try:
           
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            self.client_sockets.append(client_socket)
            client_socket.setblocking(0)

            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

            # Example: Add a message to the outgoing queue
            self.add_message("Hello from the server!")

        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    print(f"Received from {client_socket.getpeername()}: {data.decode('utf-8')}")
                    data = data.decode('utf-8')
                    if ( data.find('\n') != -1 ):
                        for line in data.split('\n'):
                            
                            if line.startswith('Client'):
                                if (line.find(',') != -1):
                                    fullCommand = line.split(',')
                                    if fullCommand[1] == "POINT_UPDATE":
                                        self.app.event_queue.put({"type": NetworkEvents.EVENT_POINT_UPDATE, "message": {"address": self.host, "message": line}})
                                    elif fullCommand[1] == "INITIALIZE_GAME":
                                        print("Client told me to initialize game")
                                        self.app.event_queue.put({"type": NetworkEvents.EVENT_INITIALIZE_GAME, "message": {"address": self.host, "message": line}})
                                    elif fullCommand[1] == "START_GAME":
                                        print("Client told me to start")
                                        self.app.event_queue.put({"type": NetworkEvents.EVENT_START, "message": {"address": self.host, "message": line}})
                                    elif fullCommand[1] == "END_GAME":
                                        print("Client told me to end game")
                                        self.app.event_queue.put({"type": NetworkEvents.EVENT_END_GAME, "message": {"address": self.host, "message": line}})
                except BlockingIOError:
                    time.sleep(0.1)

        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def message_sender(self):
        try:
            while True:
                if not self.outgoing_message_queue.empty():
                    message = self.outgoing_message_queue.get()
                    for client_socket in self.client_sockets:
                        client_socket.send(message.encode('utf-8'))
                else:
                    time.sleep(0.5)
        except Exception as e:
            print(f"Error in message sender: {e}")

    def add_message(self, message):
        self.outgoing_message_queue.put(message)

    def point_update(self, points, lives):
        message = "Server,"
        message += "POINT_UPDATE,"
        message += str(points) 
        message += ","
        message += str(lives)
        message += "\n"

        self.add_message(message)

    def send_ack(self):
        message = "Server,ACK,1\n"
        self.add_message(message)
    
    def send_end(self):
        message = "Server,END_GAME\n"
        self.add_message(message)

if __name__ == "__main__":
    server = ServerThread(host='127.0.0.1', port=12345)
    server.start()
    print("ADFASDF")
