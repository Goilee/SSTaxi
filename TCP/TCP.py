import socket
import struct
from socket import SHUT_RDWR

class TCP:
    def __init__(self,sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock
        self.targsock = None
    def __receive(self):
        chunks = []
        bytes_recd = 0
        size = ord(self.targsock.recv(1))
        while bytes_recd < size:
            chunk = self.targsock.recv(min(size - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken while receive")
            chunks.append(chunk)
            bytes_recd += len(chunk)
        return b''.join(chunks)

    def __send(self, msg):
        totalSend = 0
        self.targsock.send(bytes([len(msg)]))
        while totalSend < len(msg):
            send = self.targsock.send(msg[totalSend:])
            if send == 0:
                raise RuntimeError("socket connection broken while send")
            totalSend += send
    def waitSTR(self):
        msg = b''
        while msg == b'':
            msg = self.__receive()
        msg = msg.decode()
        self.__send("Here".encode())
        return msg

    def sendSTR(self, msg):
        self.__send(msg.encode())
        msg2 = b''
        while msg2 == b'':
            msg2 = self.__receive()
        msg2 = msg2.decode()
        if msg2 != "Here":
            self.sendSTR(msg)
    def waitINT(self):
        msg = b''
        while msg == b'':
            msg = self.__receive()
        msg = struct.unpack("i",msg)
        self.__send("Here".encode())
        return msg[0]
    def waitFloat(self):
        msg = b''
        while msg == b'':
            msg = self.__receive()
        msg = struct.unpack("f",msg)
        self.__send("Here".encode())
        return msg[0]
    def waitList(self):
        msg = b''
        while msg == b'':
            msg = self.__receive()
        msg = list(bytes(msg))
        self.__send("Here".encode())
        return msg
    def sendList(self,msg):
        self.__send(bytes(msg))
        msg2 = b''
        while msg2 == b'':
            msg2 = self.__receive()
        msg2 = msg2.decode()
        if msg2 != "Here":
            self.sendINT(msg)
    def sendINT(self,msg):
        self.__send(struct.pack("i", msg))
        msg2 = b''
        while msg2 == b'':
            msg2 = self.__receive()
        msg2 = msg2.decode()
        if msg2 != "Here":
            self.sendINT(msg)
    def sendFloat(self,msg):
        self.__send(struct.pack("f", msg))
        msg2 = b''
        while msg2 == b'':
            msg2 = self.__receive()
        msg2 = msg2.decode()
        if msg2 != "Here":
            self.sendINT(msg)
    def close(self):
        self.targsock.shutdown(SHUT_RDWR)
        self.targsock.close()