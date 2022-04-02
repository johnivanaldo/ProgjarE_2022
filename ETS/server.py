import socket
import logging
import json

alldata = dict()
alldata['1'] = dict(nomor=1, nama="Ederson", posisi="kiper")
alldata['2'] = dict(nomor=2, nama="Walker", posisi="bek kiri")
alldata['3'] = dict(nomor=3, nama="Stones", posisi="bek tengah kiri")
alldata['4'] = dict(nomor=4, nama="Laporte", posisi="bek tengah kanan")
alldata['5'] = dict(nomor=5, nama="Cancelo", posisi="bek kanan")
alldata['6'] = dict(nomor=6, nama="De Bruyne", posisi="gelandang serang tengah")
alldata['7'] = dict(nomor=7, nama="Sterling", posisi="sayap kiri")
alldata['8'] = dict(nomor=8, nama="Grealish", posisi="penyerang tengah")


def versi():
    return "versi 0.0.1"


class Server:
    def __init__(self, ip, port):
        self.sock = None
        self.ip = ip
        self.port = port

    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.ip, self.port))
        print(f"starting up on {self.ip}:{self.port}")
        self.sock.listen(1000)

    def close_socket(self):
        self.sock.close()

    def accept_connection(self):
        connection, client_address = self.sock.accept()
        print(f"accepting connection from {client_address}")
        self.handle_request(connection)

    def proses_request(self, request_string):
        cstring = request_string.split(" ")
        hasil = None
        try:
            command = cstring[0].strip()
            if (command == 'getdatapemain'):
                logging.warning("getdata")
                nomorpemain = cstring[1].strip()
                try:
                    logging.warning(f"data {nomorpemain} ketemu")
                    hasil = alldata[nomorpemain]
                except:
                    hasil = None
            elif (command == 'versi'):
                hasil = versi()
        except:
            hasil = None
        return hasil

    def serialisasi(self, a):
        # print(a)
        # serialized = str(dicttoxml.dicttoxml(a))
        serialized = json.dumps(a)
        logging.warning("serialized data")
        logging.warning(serialized)
        return serialized

    def handle_request(self, connection):
        print("handling request")
        selesai = False
        data_received = ""  # string
        while True:
            data = connection.recv(32)
            print(f"received {data}")
            if data:
                data_received += data.decode()
                print(f"decoded data {data_received}")
                if "\r\n\r\n" in data_received:
                    print("end of file")
                    selesai = True

                if (selesai):
                    hasil = self.proses_request(data_received)
                    logging.warning(f"hasil proses: {hasil}")
                    print(f"hasil proses: {hasil}")

                    hasil = self.serialisasi(hasil)
                    hasil += "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    selesai = False
                    data_received = ""  # string
                    break

            else:
                break
    print("handling request done")


if __name__ == '__main__':
    server = Server(ip='0.0.0.0', port=10000)
    print("running server no-ssl single_thread server")
    try:
        server.create_socket()
        while True:
            server.accept_connection()
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    except Exception as ee:
        print("ERROR")
        print(ee)
        logging.info(f"ERROR: {str(ee)}")
    finally:
        server.close_socket()
