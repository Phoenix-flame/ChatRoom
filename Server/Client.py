import threading


class Client(threading.Thread):
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr

    def run(self):
        self.conn.sendall(b'Welcome to this chatroom!') 
        logging.info("Client %s", str(self.addr))
        while True:
            try:
                tmp = self.conn.recv(1024)
                if tmp == b'':
                    logging.info("Client %s left us...", str(addr))
                    for i in range(len(clients)):
                        if clients[i][0] == self.addr:
                            del clients[i] # remove disconnected user
                            break
                    break
                # print(tmp)
                if len(clients) == 1:
                    self.conn.sendall(b'Nobody is in chatroom')
                for client in clients:
                    if client[1] is not self.conn:
                        client[1].sendall(tmp)
            except BrokenPipeError:
                logging.error("Broken Pipe Error [Client %s]", str(addr))
                break
            except KeyboardInterrupt:
                soc.close()
                break
