import datetime
import json
import os
import socket
from cipher_factory import CipherFactory
from hamming import Hamming
from ldpc import LDPC
from rs import RS


class Backend:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.tcp_port_1 = 5000
        self.tcp_port_2 = 5001
        self.udp_port_1 = 5002
        self.udp_port_2 = 5003
        self.host2 = None
        self.filename = f'history_{self.host}.json'
        self.history_dict = self._load_history_to_dict()
        self.receiving_tcp_socket = None
        self.receiving_udp_socket = None
        self.algorithm_types = ["Код Хэминга", "LDPC", "Код Кердока"]

    def _load_history_to_dict(self):
        if not os.path.exists(self.filename):
            history_json = {'messages': []}
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(history_json, file)
        else:
            with open(self.filename, "r", encoding='utf-8') as file:
                history_json = json.loads(file.read())
        return history_json

    def run_receiving(self, gui_text):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            udp_socket.bind((self.host, self.udp_port_2))
            while True:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                    tcp_socket.bind((self.host, self.tcp_port_2))
                    tcp_socket.listen(1)
                    conn, tcp_addr = tcp_socket.accept()
                    with conn:
                        while True:
                            try:
                                algorithm_type_info, _ = conn.recvfrom(1024)
                                algorithm_type = algorithm_type_info.decode('utf-8')
                                data, udp_addr = udp_socket.recvfrom(6144)
                                encode_message = data.decode('utf-8')
                                if tcp_addr[0] == udp_addr[0] and algorithm_type != '' and encode_message != '':
                                    if algorithm_type == self.algorithm_types[0]:
                                        decoded_message = CipherFactory.decode(Hamming, encode_message)
                                    elif algorithm_type == self.algorithm_types[1]:
                                        decoded_message = CipherFactory.decode(LDPC, encode_message)
                                    elif algorithm_type == self.algorithm_types[2]:
                                        decoded_message = CipherFactory.decode(RS, encode_message)
                                    else:
                                        break
    
                                    self._write_to_history(decoded_message, encode_message, algorithm_type, udp_addr[0], self.host)
                                    gui_text.insert_message(self.history_dict['messages'][-1])
                                break
                            
                            except OSError:
                                return

    def send(self, text_message, encode_message, alg_type):
        if encode_message:
            with (
                socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket,
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket
            ):
                try:
                    tcp_socket.connect((self.host2, self.tcp_port_1))
                    tcp_socket.sendall(alg_type.encode())
                    udp_socket.sendto(encode_message.encode('utf-8'), (self.host2, self.udp_port_1))
                    self._write_to_history(text_message, encode_message, alg_type, self.host, self.host2)
                except TypeError:
                    return 1
                except socket.gaierror:
                    return 2

    def _write_to_history(self, text_message, code_message, algorithm, sender, receiver):
        data = {
            'time': str(datetime.datetime.now()),
            'sender': sender,
            'receiver': receiver,
            'text': text_message,
            'code_message': code_message,
            'algorithm': algorithm
        }
        self.history_dict['messages'].append(data)
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(self.history_dict, file)
            file.write('\n')
