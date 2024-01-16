import socket
import threading
import queue

from include.defines import NetworkEvents

class ClientThread:
    def __init__(self, host='activateMotor.local', port=12345, app=None):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.outgoing_message_queue = queue.Queue()
        self.app = app

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))

            # Start the message sender thread
            sender_thread = threading.Thread(target=self.message_sender)
            sender_thread.start()

            # Start the message receiver thread
            receiver_thread = threading.Thread(target=self.message_receiver)
            receiver_thread.start()

        except Exception as e:
            print(f"Error connecting to server: {e}")

    def message_sender(self):
        try:
            while True:
                if not self.outgoing_message_queue.empty():
                    message = self.outgoing_message_queue.get()
                    self.client_socket.send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error in message sender: {e}")

    def message_receiver(self):
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                print(f"Received from server: {data.decode('utf-8')}")
                data = data.decode('utf-8')
                if ( data.find('\n') != -1 ):
                    for line in data.split('\n'):
                        
                        if line.startswith('Server'):
                            if (line.find(',') != -1):
                                fullCommand = line.split(',')
                                if fullCommand[1] == "POINT_UPDATE":
                                    self.app.event_queue.put({"type": NetworkEvents.EVENT_POINT_UPDATE, "message": {"address": self.host, "message": line}})
                                elif fullCommand[1] == "LIFE_UPDATE":
                                    self.app.event_queue.put({"type": NetworkEvents.EVENT_LIFE_UPDATE, "message": {"address": self.host, "message": line}})
                                elif fullCommand[1] == "ACK":
                                    self.app.event_queue.put({"type": NetworkEvents.EVENT_ACK, "message": {"address": self.host, "message": line}})
        except Exception as e:
            print(f"Error in message receiver: {e}")

    def send_message(self, message):
        self.outgoing_message_queue.put(message)

    def close(self):
        try:
            self.client_socket.close()
        except Exception as e:
            print(f"Error closing connection: {e}")