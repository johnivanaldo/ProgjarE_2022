import socket
import logging
import threading
import ssl
import os
import random
import datetime


class Request:
    def __init__(self, ip, port, data, secure=False):
        self.ip = ip
        self.port = port
        self.data = data
        self.secure = secure
        self.response_success = False

    def make_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (self.ip, self.port)
        logging.warning(f"connecting to {server_address}")
        self.sock.connect(server_address)

    def make_secure_socket(self):
        try:
            # get it from https://curl.se/docs/caextract.html
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.verify_mode = ssl.CERT_OPTIONAL
            context.load_verify_locations(os.getcwd() + '/domain.crt')

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_address = (self.ip, self.port)
            logging.warning(f"connecting to {server_address}")
            self.sock.connect(server_address)
            secure_socket = context.wrap_socket(
                self.sock, server_hostname=self.ip)
            logging.warning(secure_socket.getpeercert())
            self.sock = secure_socket

        except Exception as ee:
            logging.warning(f"error {str(ee)}")

    def send(self):
        if(self.secure):
            self.make_secure_socket()
        else:
            self.make_socket()
        print(f"sending {self.data}")
        self.sock.sendall(self.data.encode())
        self.handle_response()

    def handle_response(self):
        amount_received = 0
        amount_expected = len(self.data)
        while amount_received < amount_expected:
            self.response_success = True
            data = self.sock.recv(16)
            amount_received += len(self.data)
            print(f"response : {data}")
            logging.info(f"{data}")

    def send_with_thread(self):
        self.thread = threading.Thread(target=self.send, args=())
        self.thread.start()

    def join_thread(self):
        self.thread.join()


def send_random_request(secure):
    id_pemain = random.randint(1, 10)
    request = Request(
        ip='172.16.16.101',
        port=10000,
        data=f"getdatapemain {id_pemain}\r\n\r\n",
        secure=secure
    )
    return request


try:
    thread_count = 20
    secure = True
    response_count = 0

    if(secure):
        print(f"running ssl multi thread (with {thread_count} thread)")
    else:
        print(f"running no-ssl multi thread (with {thread_count} thread)")

    requests = dict()

    catat_awal = datetime.datetime.now()

    for thread in range(thread_count):
        requests[thread] = send_random_request(secure)
        requests[thread].send_with_thread()

    for thread in range(thread_count):
        requests[thread].join_thread()

    for thread in range(thread_count):
        if(requests[thread].response_success):
            response_count += 1

    catat_akhir = datetime.datetime.now()
    selesai = catat_akhir - catat_awal

    print(f"jumlah request: {thread_count}")
    print(f"jumlah response: {response_count}")

    print(f"client selesai dengan {selesai} ms")

except Exception as ee:
    logging.info(f"ERROR: {str(ee)}")
    exit(0)
finally:
    logging.info("closing")
