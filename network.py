from socket import socket, AF_INET, SOCK_DGRAM, inet_aton, inet_ntoa
import random, time
import threading, queue
from socketserver import ThreadingUDPServer
from util.RDTSegment import RDTSegment
lock = threading.Lock()


def bytes_to_addr(bytes):
    return inet_ntoa(bytes[:4]), int.from_bytes(bytes[4:8], 'big')


def addr_to_bytes(addr):
    return inet_aton(addr[0]) + addr[1].to_bytes(4, 'big')

# corrupt:
def corrupt(data: bytes) -> bytes:
    raw = list(data)
    for _ in range(0, random.randint(0, 3)):
        pos = random.randint(0, len(raw) - 1)
        raw[pos] = random.randint(0, 255)
    return bytes(raw)


class Server(ThreadingUDPServer):
    def __init__(self, addr, rate=None, delay=None, corrupt=None):
        super().__init__(addr, None)
        self.rate = rate
        self.buffer = 0
        self.delay = delay
        self.corrupt = corrupt
        self.corrupt_rate = 0.00001

    def verify_request(self, request, client_address):
        """
        request is a tuple (data, socket)
        data is the received bytes object
        socket is new socket created automatically to handle the request

        if this function returns False， the request will not be processed, i.e. is discarded.
        details: https://docs.python.org/3/library/socketserver.html
        """
        if self.buffer < 100000:  # some finite buffer size (in bytes)
            self.buffer += len(request[0])
            return True
        else:
            return False

    def finish_request(self, request, client_address):
        data, socket = request

        with lock:
            if self.rate: time.sleep(len(data) / self.rate)
            self.buffer -= len(data)
            """
            blockingly process each request
            you can add random loss/corrupt here

            for example:
            if random.random() < loss_rate:
                return 
            for i in range(len(data)-1):
                if random.random() < corrupt_rate:
                    data[i] = data[:i] + (data[i]+1).to_bytes(1,'big) + data[i+1:]
            """

        """
        this part is not blocking and is executed by multiple threads in parallel
        you can add random delay here, this would change the order of arrival at the receiver side.
        
        for example:
        time.sleep(random.random())
        """

        # random delay
        time.sleep(random.random()/5)
        # corrupt
        for i in range(len(data)-1):
            if random.random() < self.corrupt_rate:
                data = data[:i] + (data[i] + 1).to_bytes(1, 'big') + data[i+1:]






        to = bytes_to_addr(data[:8])
        print(client_address, to)  # observe tht traffic
        socket.sendto(addr_to_bytes(client_address) + data[8:], to)


server_address = ('127.0.0.1', 12345)

if __name__ == '__main__':
    with Server(server_address, rate=20000) as server:
        server.serve_forever()
