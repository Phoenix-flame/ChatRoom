import argparse as arg 
import socket
import threading
from collections import deque
import logging
from SocketServer import SocketServer
import Colorer

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

print("Server")

def argumentPars():
    parser = arg.ArgumentParser(add_help=True)
    parser.add_argument("-sip", help="IP Address", type=str)
    parser.add_argument("-sp", help="Port Number", type=str)
    args = parser.parse_args()
    if(args.sip == None and args.sp != None):
        return args.sp, "127.0.0.1"
    elif(args.sp == None and args.sip != None):
        return 30008, args.sip
    elif(args.sp == None and args.sip == None):
        return 30008, "127.0.0.1"
    return args.sp, args.sip


if __name__ == "__main__":
    port, ip = argumentPars()
    logging.warn("Server IP:[%s], Port:[%s]", ip, port)
    
    server = SocketServer(ip=ip, port=port)
    server.start()
    try:
        while True:
            continue
    except KeyboardInterrupt:
        print('\nWait...')
        server.stop()
        server.join()
        if server.soc:
            server.soc.close()
        print('End.')
