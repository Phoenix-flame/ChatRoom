from threading import Thread
import threading
import socket
from ClientHandler import ClientHandler, clients, client_threads
import logging

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


class SocketServer(Thread):
    def __init__(self, ip = "127.0.0.1", port=30008):
        Thread.__init__(self)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.soc.bind((ip, int(port)))
        self.soc.listen()

    def close(self):
        for t in client_threads:
            t.stop()
            t.join()
        
        if self.soc:
            self.soc.close()

    def run(self):
        self.__stop = False
        while not self.__stop:
            self.soc.settimeout(1)
            try:
                connection, addr = self.soc.accept()
                logging.info("Client %s joined.", str(addr))
                if len(clients) == 1:
                    self.notify()
                clients.append([addr, connection])
            except socket.timeout:
                connection = None # TODO #1
 
            if connection:
                client_thread = ClientHandler(connection, addr)
                client_threads.append(client_thread)
                client_thread.start()
        self.close()
 
    def stop(self):
        self.__stop = True

    def notify(self):
        clients[0][1].sendall(b'New User joined the group')


