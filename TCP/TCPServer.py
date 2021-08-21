import socket


class ServerSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def receive(self):
        chunks = []
        bytes_recd = 0
        size = ord(self.clisock.recv(1))
        while bytes_recd < size:
            chunk = self.clisock.recv(min(size - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken while receive")
            chunks.append(chunk)
            bytes_recd += len(chunk)
        return b''.join(chunks)

    def send(self, msg):
        totalSend = 0
        self.clisock.send(bytes([len(msg)]))
        while totalSend < len(msg):
            send = self.clisock.send(msg[totalSend:])
            if send == 0:
                raise RuntimeError("socket connection broken while send")
            totalSend += send

    def startingCon(self, ip, port, wlcMsg):
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.startingCon()
        print("connection started")
        while True:
            (self.clisock, address) = self.sock.accept()
            msg = self.receive().decode()
            if msg == wlcMsg:
                self.send("Hi")
                print("connected")
            else:
                raise RuntimeError("wrong answer")
                continue
            break

    def waitMSG(self):
        msg = b''
        while msg == b'':
            msg = self.receive()
        msg = msg.decode()
        self.send("Here")
        print(msg)
        return msg

    def sendMSG(self, msg):
        self.send(msg)
        msg2 = b''
        while msg2 == b'':
            msg2 = self.receive()
        msg2 = msg2.decode()
        if msg2 == "Here":
            print("Here")
        else:
            self.sendMSG(msg)
    def getCrossId(self):
        id = self.waitMSG()
        return int(id)
    def getWay(self):
        self.sendMSG("Way")
        msg = self.waitMSG()
        return msg.split()
    def sendStopSign(self):
        self.sendMSG("Done")
        print("done sended")
    def sendDirection(self, direction):
        self.sendMSG(direction)
        print("direction is " + direction)

