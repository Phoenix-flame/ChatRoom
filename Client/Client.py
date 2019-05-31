from threading import Thread
import threading
import select
import socket
import logging
import argparse as arg 
import sys

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


def argumentPars():
    parser = arg.ArgumentParser(add_help=True)
    parser.add_argument("-sip", help="IP Address", type=str)
    parser.add_argument("-sp", help="Port Number", type=str)
    args = parser.parse_args()
    if(args.sip == None):
        return args.sp, "127.0.0.1"
    return args.sp, args.sip


class Client(Thread):
    def __init__(self, ip="127.0.0.1", port=30008):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_thread = Recv(self.soc)
        try:
            self.soc.connect((ip, int(port)))
            self.recv_thread.start()
        except ConnectionRefusedError:
            logging.error("Server is not available")
            exit(0)

    def close(self):
        if self.soc:
            self.soc.close()
            self.soc = -1

    def run(self):
        self.__stop = False
        while not self.__stop:
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                line = sys.stdin.readline()
                if line:
                    self.soc.sendall(line[:-1].encode())
                else: # an empty line means stdin has been closed
                    print('eof')
                    exit(0)
            
        self.close()
 
    def stop(self):
        self.__stop = True


class Recv(Thread):
    def __init__(self, soc):
        Thread.__init__(self)
        self.soc = soc

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
                        incoming_data = self.soc.recv(1024) # TODO #3
                    except ConnectionResetError:
                        logging.error("Connection Reset Error")
                    # Check if socket has been closed
                    if incoming_data == b'':
                        logging.info("Client %s left us...", str('b'))
                        self.stop()
                    else:
                        logging.info("Received [%s]", incoming_data.decode())
        self.close()
 
    def stop(self):
        self.__stop = True
 
    def close(self):
        return
        if self.soc:
            self.soc.close()
            self.soc = -1


if __name__ == '__main__':
    port, ip = argumentPars()
    logging.info("Client IP:[%s], Port:[%s]", ip, port)
    
    client = Client(ip=ip, port=port)
    client.start()
    try:
        while True:
            continue
    except KeyboardInterrupt:
        print('\nWait...')
        client.stop()
        client.join(2)