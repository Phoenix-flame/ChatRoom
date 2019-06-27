from flask import render_template, request, url_for
import flask
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
import requests


app = flask.Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

format = "%(asctime)s: %(message)s"
log.basicConfig(format=format, level=log.INFO, datefmt="%H:%M:%S")


data = []
isfromother = None
send_msg = []

class Client(Thread):
    def __init__(self, ip="127.0.0.1", port=30008):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_thread = Recv(self.soc)
        self.__BUFFER_SIZE = 1024
        self.prev_val = ""
        try:
            self.soc.connect((ip, int(port)))
            print("Server cnnected.")
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
            if len(send_msg) > 0:
                if send_msg[len(send_msg) - 1]["msg"] != self.prev_val:
                    self.prev_val = send_msg[len(send_msg) - 1]["msg"]
                    self.soc.sendall(self.prev_val.encode())     
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
        print()
        print("Here")
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
                        with app.app_context():
                            my_form_post(msg={"msg":msg, "ip":"Server", "other":True}, other=True) 
                            add_data({"msg":msg, "ip":"127.0.0.1", "other":True})
                        log.info("From Server: %s", msg)
                    else :
                        with app.app_context():
                            my_form_post(msg={"msg":msg, "ip":str(port), "other":True}, other=True) 
                            add_data({"msg":msg, "ip":"127.0.0.1", "other":True})

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

@app.before_request
def before_request():
    # When you import jinja2 macros, they get cached which is annoying for local
    # development, so wipe the cache every request.
    if 'localhost' in request.host_url or '0.0.0.0' in request.host_url:
        app.jinja_env.cache = {}

@app.route('/')
def main(a = None, b = None):
    print(a, b)
    # url_for('static', filename='css/bootstrap.min.css')
    tmp = [data[i] for i in range(len(data) - 1, -1, -1)]
    return render_template('GClient.html', data=tmp, isfromother=isfromother)

@app.route('/<msg>/<other>', methods=['POST'])
def my_form_post(msg = None, other = False):
    if other:
        print("From Others")
        data.append(msg)
    else:
        print("From yourself")
        text = request.form['text']
        send_msg.append({"msg":text, "ip":"127.0.0.1", "other":False})
        data.append({"msg":text, "ip":"127.0.0.1", "other":False})
    tmp = [data[i] for i in range(len(data) - 1, -1, -1)]
    return render_template('GClient.html', data = tmp)

# @app.route('/')
def add_data(d):
    return flask.jsonify(result=d)
client = Client()
client.start()


