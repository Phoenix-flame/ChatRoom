from flask import Flask
from flask_socketio import SocketIO, emit, send
from threading import Lock
import os
from threading import Thread
import threading
import select
import socket
import logging as log
import argparse as arg 
import sys
from protoc import Server_pb2
from google.protobuf.message import DecodeError
import Colorer


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread = None
thread_lock = Lock()


format = "%(asctime)s: %(message)s"
log.basicConfig(format=format, level=log.INFO, datefmt="%H:%M:%S")

received_msg = []


class Client_thread(Thread):
    def __init__(self, ip="127.0.0.1", port=30008):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        log.warn("port: " + str(port))
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_thread = Recv(self.soc)
        self.__BUFFER_SIZE = 1024
        self.prev_val = ""
        try:
            self.soc.connect((ip, int(port)))
            self.recv_thread.start()
        except ConnectionRefusedError:
            log.error("Server is not available")
            exit(0)

    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1

    def run(self):
        self.__stop = False
        while not self.__stop:
            # print(len(received_msg))
            if len(received_msg) > 0:
                # print(len(received_msg))
                if received_msg[len(received_msg) - 1]["msg"] != self.prev_val:
                    self.prev_val = received_msg[len(received_msg) - 1]["msg"]
                    self.soc.sendall(self.prev_val.encode())    
                    log.warn("message is sent") 
        self.close()
 
    def stop(self):
        self.__stop = True


class Recv(Thread):
    def __init__(self, soc):
        Thread.__init__(self)
        self.soc = soc
        self.__BUFFER_SIZE = 1024

    def run(self):
        self.__stop = False
        while not self.__stop:
                try:
                    ready, _, _ = select.select([self.soc,], [self.soc,], [], 5)
                except select.error:
                    self.stop()
                    return
                except ValueError:
                    break
                if len(ready) > 0:
                    incoming_data = b''
                    try:
                        incoming_data = self.soc.recv(self.__BUFFER_SIZE) # TODO #3
                    except ConnectionResetError:
                        log.error("Connection Reset Error")
                    # Check if socket has been closed
                    if incoming_data == b'':
                        log.info("Server disconnected.")
                        self.stop()
                    else:
                        ip, port, msg = self.messageCallback(incoming_data)
                        if ip == "Server":
                            socketio.emit('my response',
                            {'ip': str(ip) + ":" + str(port), 'content': msg, 'fromOthers': True})
                            log.info("From Server: %s", msg)
                        else :
                            socketio.emit('my response', 
                            {'ip': str(ip) + ":" + str(port), 'content': msg, 'fromOthers': True})
                            log.info("From <(%s, %s)> %s!", ip, port, msg)
        self.close()
 
    def messageCallback(self, data):
        incoming_data = Server_pb2.Client()
        try:
            incoming_data.ParseFromString(data)
        except DecodeError:
            print(2)
        return incoming_data.name, incoming_data.port, incoming_data.msg

    def stop(self):
        self.__stop = True
 
    def isStopped(self) -> bool:
        return self.__stop
    
    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1




