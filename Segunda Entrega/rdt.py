from socket import *
from utils import checksum
import time

class RDT:

    def __init__(self, addressPort = ("127.0.0.1", 20001), bufferSize = 1024, isServer = 0):
        self.sender_addr = 0
        self.seq_num = 0
        self.addressPort =  addressPort
        self.bufferSize = bufferSize
        self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
        if(isServer):
            self.UDPSocket.bind(self.addressPort)
            self.UDPSocket.settimeout(2.0)
            print("Server running")
        else:
            print("Client running")
    
    #def send(self, data):
    #        self.send_pkg(data)

    def send_pkg(self, data):
        data = self.create_header(data)
        ack = False

        while not ack:
            self.UDPSocket.sendto(data, self.addressPort)

            try:
                data, self.sender_addr = self.rcv_pkg(self.bufferSize)
            except socket.timeout:
                print("Did not receive ACK. Sending again.")
            else:
                ack = self.rcv_ack(data)

    def receive(self):
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
        ack, data = self.rcv_pkg(data)

        if ack == True:
            self.send_ack(1)
        else:
            self.send_ack(0)

        buffer = str(data)
        
        while data:
            data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
            buffer += str(data)

    def send_ack(self, ack):
        if ack == True:
            data = self.create_header("ACK".encode())
        else:
            data = self.create_header("NACK".encode())

        self.send_pkg(data)

    def rcv_pkg(self, data):
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        if self.checksum_(checksum, payload) and seq_num == self.seq_num:
            self.seq_num = 1 - self.seq_num
            return (True, payload)
        else:
            return (False, payload)
    

    def rcv_ack(self, data):
        seq_num = data['seq']
        checksum = data['checksum']
        payload = data['payload']

        if self.checksum_(checksum, payload) and seq_num == self.seq_num and payload.decode() == "ACK":
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

        return {
            'seq': self.seq_num,
            'checksum': chcksum,
            'payload' : data
        }




    


