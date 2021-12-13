from socket import *
from utils import checksum
import time


class RDTServer:
    def __init__(self, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
        self.sender_addr = 0
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.UDPSocket.bind(self.addressPort)
        #self.UDPSocket.settimeout(2.0)
        self.lista_usuarios = []
        self.lista_seq = {}
        print("Server running")
        self.run()

    def run(self):
        while(1):
            self.receive()
    
    def send(self, data, sender_addr):
        #print("Sending to client")
        self.UDPSocket.sendto(data, sender_addr)

    def send_pkg(self, data, sender_addr):
        data = self.create_header(data, sender_addr)
        ack = False

        self.UDPSocket.settimeout(2.0)
        rcv_addr = 0
        while not ack:
            self.send(data, sender_addr)
            try:
                data, rcv_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except socket.timeout:
                print("Did not receive ACK. Sending again.")
            else:
                ack = self.rcv_ack(data, sender_addr)

        self.UDPSocket.settimeout(None)


    def new_connection(self, nome, sender_addr):
        self.lista_usuarios.append((sender_addr, nome))
        self.lista_seq.update({sender_addr: 0})

    def broadcast_new_user(self, nome):
        data = nome + " entrou na sala"
        for x in self.lista_usuarios:
            #print(x)
            self.send_pkg(data, x[0])


    def receive(self):
        #print("Receveing package")
        data, sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        #print("pkg received")
        data = self.rcv_pkg(data, sender_addr)

        #print("Received")
        return data.encode()

    def send_ack(self, ack, sender_addr):
        if ack:
            #print("Sending ACK")
            data = self.create_header("ACK", sender_addr)
        else:
            #print("Sending NACK")
            data = self.create_header("NACK", sender_addr)
        self.send(data, sender_addr)


    def rcv_pkg(self, data, sender_addr):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        print(data)
        x, y = payload.split()

        if(x == "new_connection"):
            #print("new_connection")
            if self.checksum_(checksum, payload):
                self.new_connection(y, sender_addr)
                self.send_ack(1, sender_addr)
                self.lista_seq.update({sender_addr: 1})
                self.broadcast_new_user(y)
                return payload
            else:
                self.send_ack(0, sender_addr)
                return ""
            

        if(self.lista_seq.get(sender_addr) != None):
            seq = self.lista_seq.get(sender_addr)
        else:
            self.send_ack(0, sender_addr)
            return ""

        if self.checksum_(checksum, payload) and seq_num == seq:
            self.send_ack(1, sender_addr)
            self.lista_seq.update({sender_addr: 1-seq})
            return payload
        else:
            self.send_ack(0, sender_addr)
            return ""
    

    def rcv_ack(self, data, sender_addr):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        if(self.lista_seq.get(sender_addr) != None):
            seq = self.lista_seq.get(sender_addr)
        else:
            return False

        if self.checksum_(checksum, payload) and seq_num == seq and payload == "ACK":
            self.lista_seq.update({sender_addr: 1-seq})
            return True
        else:
            return False


    def checksum_(self, chcksum, payload):
        if checksum(payload) == chcksum:
            return True
        else:
            return False


    def create_header(self, data, sender_addr):

        chcksum = checksum(data)
        seq = self.lista_seq.get(sender_addr)
        return str({
            'seq': seq,
            'checksum': chcksum,
            'payload' : data
        }).encode()

    def close_connection(self):
        print("Closing socket")
        self.UDPSocket.close()


class RDTClient:

    def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
        self.sender_addr = 0
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        self.isServer = isServer
        self.seq_num = 0
        self.UDPSocket.settimeout(2.0)
        print("Entre com seu nome:")
        self.nome = input()
        data = "new_connection " + self.nome
        self.send_pkg(data.encode())
    
    def send(self, data):
        #print("Sending to server")
        self.UDPSocket.sendto(data, self.addressPort)

    def send_pkg(self, data):
        data = self.create_header(data.decode())
        ack = False
        self.UDPSocket.settimeout(2.0)
        while not ack:
            self.send(data)

            try:
                data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
            except socket.timeout:
                print("Did not receive ACK. Sending again.")
            else:
                ack = self.rcv_ack(data)

    def always_rcv(self):
        #print("Receveing package")
        self.UDPSocket.settimeout(None)
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        self.UDPSocket.settimeout(2.0)
        data = self.rcv_pkg(data)

        #print("Received")
        return data.encode()

    def receive(self):
        #print("Receveing package")
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        data = self.rcv_pkg(data)

        #print("Received")
        return data.encode()

    def send_ack(self, ack):
        if ack:
            data = self.create_header("ACK")
        else:
            data = self.create_header("NACK")
        self.send(data)


    def rcv_pkg(self, data):
        
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        #print("rck_pkg: ")
        #print(data)

        if self.checksum_(checksum, payload) and seq_num == self.seq_num:
            self.send_ack(1)
            self.seq_num = 1 - self.seq_num
            return payload
        else:
            self.send_ack(0)
            return ""
    

    def rcv_ack(self, data):
        data = eval(data.decode())
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        #print("rck_ack: ")
        #print(data)
        
        
        if self.checksum_(checksum, payload) and seq_num == self.seq_num and payload == "ACK":
            self.seq_num = 1 - self.seq_num
            return True
        else:
            return False


    def checksum_(self, chcksum, payload):
        if checksum(payload) == chcksum:
            return True
        else:
            return False


    def create_header(self, data):

        chcksum = checksum(data)

        return str({
            'seq': self.seq_num,
            'checksum': chcksum,
            'payload' : data
        }).encode()

    def close_connection(self):
        print("Closing socket")
        self.UDPSocket.close()




    


