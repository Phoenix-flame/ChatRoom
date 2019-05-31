import numpy as np 
import argparse as arg 
import socket
import threading
from collections import deque
import logging

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

print("Server")

def argumentPars():
    parser = arg.ArgumentParser(add_help=True)
    parser.add_argument("-sip", help="IP Address", type=str)
    parser.add_argument("-sp", help="Port Number", type=str)
    args = parser.parse_args()
    if(args.sip == None):
        return args.sp, "127.0.0.1"
    return args.sp, args.sip

clients = []
incomming_messages = deque()
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    port, ip = argumentPars()
    logging.info("Server IP:[%s], Port:[%s]", ip, port)

    client_manager = threading.Thread(target=clientManager)
    soc.bind((ip, int(port)))
    client_manager.start()

def Client(addr, conn):
    conn.sendall(b'Welcome to this chatroom!') 
    logging.info("Client %s", str(addr))
    while True:
        try:
            tmp = conn.recv(1024)
            if tmp == b'':
                logging.info("Client %s left us...", str(addr))
                for i in range(len(clients)):
                    if clients[i][0] == addr:
                        del clients[i] # remove disconnected user
                        break
                break
            # print(tmp)
            if len(clients) == 1:
                conn.sendall(b'Nobody is in chatroom')
            for client in clients:
                if client[1] is not conn:
                    client[1].sendall(tmp)
        except BrokenPipeError:
            logging.error("Broken Pipe Error [Client %s]", str(addr))
            break
        except KeyboardInterrupt:
            soc.close()
            break


def clientManager():
    while True:
        try:
            soc.listen()
            conn, addr = soc.accept()
            print(len(clients))
            if len(clients) == 1:
                notify()
            
            clients.append([addr, conn])
            threading.Thread(target=Client, args = (addr, conn, )).start()
        except BrokenPipeError:
            logging.error("Broken Pipe Error [Client Manager]")
            break
        except KeyboardInterrupt:
            soc.close()
            break

def notify():
    clients[0][1].sendall(b'New User joined the group')

if __name__ == "__main__":
    main()
