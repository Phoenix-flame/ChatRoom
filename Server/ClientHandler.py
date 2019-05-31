import socket
import select
import time
from threading import Thread
import logging


format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

clients = []
client_threads = []

class ClientHandler(Thread):
    def __init__(self, connection, addr):
        Thread.__init__(self)
        connection.sendall(b'Welcome to my chatroom.') 
        self.connection = connection
        self.addr = addr
 
    def run(self):
        self.__stop = False
        while not self.__stop:
            if self.connection:
                # Check if the client is still connected and if data is available:
                try:
                    ready, _, _ = select.select([self.connection,], [self.connection,], [], 5)
                except select.error as err:
                    print(err)
                    self.stop()
                    return
 
                if len(ready) > 0:
                    incoming_data = b''
                    try:
                        incoming_data = self.connection.recv(1024) # TODO #2
                    except ConnectionResetError:
                        logging.error("Connection Reset Error")
                    # Check if socket has been closed
                    if incoming_data == b'':
                        logging.info("Client %s left us...", str(self.addr))
                        # for c in clients:
                        #     print(c[0])
                        for i in range(len(clients)):
                            if clients[i][0] == self.addr:
                                # print('Delete', clients[i][0])
                                del clients[i] # remove disconnected user
                                break
                        self.stop()
                    else:
                        logging.info("Received [%s] from Client [%s]", incoming_data.decode(), str(self.addr))
                        if len(clients) == 1:
                            clients[0][1].sendall(b'Nobody is in chatroom')
                        for c in clients:
                            if c[0] != self.addr:
                                c[1].sendall(incoming_data)
            else:
                print("No client is connected, SocketServer can't receive data")
                self.stop()
        self.close()
 
    def stop(self):
        self.__stop = True
 
    def close(self):
        if self.connection:
            self.connection.close()
