import socket 
from _thread import *
import sys
from collections import defaultdict as df
import time

class Server:
    def __init__(self):
        self.rooms = df(list)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def accept_connections(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.server.bind((self.ip_address, int(self.port)))
        self.server.listen(100)
        print(f"Server started on {self.ip_address}:{self.port}")
        print(f"Waiting for connections...")

        while True:
            connection, address = self.server.accept()
            print(str(address[0]) + ":" + str(address[1]) + " Connected")
            start_new_thread(self.clientThread, (connection,))

        self.server.close()
    
    def clientThread(self, connection):
        user_id = connection.recv(1024).decode().replace("User ", "")
        room_id = connection.recv(1024).decode().replace("Join ", "")

        if room_id not in self.rooms:
            connection.send("New Group created".encode())
            print(f"New room '{room_id}' created by {user_id}")
        else:
            connection.send("Welcome to chat room".encode())
            print(f"{user_id} joined room '{room_id}'")

        self.rooms[room_id].append(connection)

        while True:
            try:
                message = connection.recv(1024)
                if message:
                    if str(message.decode()) == "FILE":
                        self.broadcastFile(connection, room_id, user_id)
                    else:
                        message_to_send = "<" + str(user_id) + "> " + message.decode()
                        self.broadcast(message_to_send, connection, room_id)
                else:
                    self.remove(connection, room_id)
            except Exception as e:
                print(repr(e))
                print("Client disconnected earlier")
                break
    
    def broadcastFile(self, connection, room_id, user_id):
        file_name = connection.recv(1024).decode()
        lenOfFile = connection.recv(1024).decode()
        for client in self.rooms[room_id]:
            if client != connection:
                try: 
                    client.send("FILE".encode())
                    time.sleep(0.1)
                    client.send(file_name.encode())
                    time.sleep(0.1)
                    client.send(lenOfFile.encode())
                    time.sleep(0.1)
                    client.send(user_id.encode())
                except:
                    client.close()
                    self.remove(client, room_id)

        total = 0
        while str(total) != lenOfFile:
            data = connection.recv(1024)
            total = total + len(data)
            for client in self.rooms[room_id]:
                if client != connection:
                    try: 
                        client.send(data)
                    except:
                        client.close()
                        self.remove(client, room_id)
        print(f"File '{file_name}' sent to room '{room_id}'")

    def broadcast(self, message_to_send, connection, room_id):
        for client in self.rooms[room_id]:
            if client != connection:
                try:
                    client.send(message_to_send.encode())
                except:
                    client.close()
                    self.remove(client, room_id)
    
    def remove(self, connection, room_id):
        if connection in self.rooms[room_id]:
            self.rooms[room_id].remove(connection)

if __name__ == "__main__":
    # دریافت پورت از خط فرمان
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 12345  # پورت پیش‌فرض
    
    ip_address = "127.0.0.1"
    
    s = Server()
    s.accept_connections(ip_address, port)