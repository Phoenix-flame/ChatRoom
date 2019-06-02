from threading import Thread
import threading
import socket
from ClientHandler import ClientHandler, clients, client_threads
import logging as log
from protoc import Server_pb2

format = "%(asctime)s: %(message)s"
log.basicConfig(format=format, level=log.INFO, datefmt="%H:%M:%S")


class SocketServer(Thread):
    def __init__(self, ip = "127.0.0.1", port=30008):
        Thread.__init__(self)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip = ip
        self.port = port
        try:
            self.soc.bind((ip, int(port)))
        except OSError:
            log.error("Something goes wrong.")
            log.info("Try another IP or Port number.")
            exit(0)
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
                log.info("Client %s joined.", str(addr))
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

    def messageCallbackServer(self, data, ip, port):
        message = Server_pb2.Client()
        message.msg = data
        message.name = ip
        message.port = int(port)
        return message

    def notify(self):
        clients[0][1].sendall(bytes(self.messageCallbackServer("New User joined the group.", "Server", 30005).SerializeToString())) 


