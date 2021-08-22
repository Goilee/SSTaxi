import socket

class TCP:
    def __init__(self,sock=None):
        if sock is None:
            self.targsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.targsock = sock
        self.targsock = None
        self.ipServer = '127.0.0.1'
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
        self.targsock.__send(bytes([len(msg)]))
        while totalSend < len(msg):
            send = self.targsock.__send(msg[totalSend:])
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
        msg = int.from_bytes(msg)
        self.__send("Here".encode())
        return msg
    def waitList(self):
        msg = b''
        while msg == b'':
            msg = self.__receive()
        msg = list(bytes(msg))
        self.__send("Here".encode())
        return msg
    def sendINT_List(self,msg):
        self.__send(bytes(msg))
        msg2 = b''
        while msg2 == b'':
            msg2 = self.__receive()
        msg2 = msg2.decode()
        if msg2 != "Here":
            self.sendINT(msg)