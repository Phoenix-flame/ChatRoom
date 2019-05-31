import numpy as np 
import argparse as arg 
import socket
import threading
import logging
import time

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

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    port, ip = argumentPars()

    recv_thread = threading.Thread(target=Recv)
    try:
        soc.connect((ip, int(port)))
    except ConnectionRefusedError:
        logging.error("Server is not available")
        exit(0)
    recv_thread.start()

    while True:
        try:
            tmp = str(input())
            soc.sendall(tmp.encode())
        except KeyboardInterrupt:
            recv_thread.join()
            soc.close()
        except EOFError:
            recv_thread.join()
            soc.close()
            break

def Recv():
    while True:
        try:
            data = soc.recv(1024)
            # data = '5'
            # time.sleep(5)
            if data == b'':
                break
            logging.info("Received: %s", (data.decode()))
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
