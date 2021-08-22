import socket
class ClientSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def receive(self):
        chunks = []
        bytes_recd = 0
        size = ord(self.sock.recv(1))
        while bytes_recd < size:
            chunk = self.sock.recv(min(size-bytes_recd,2048))
            if chunk == b'':
                raise RuntimeError("socket connection broken while receive")
            chunks.append(chunk)
            bytes_recd += len(chunk)
        return b''.join(chunks)

    def send(self, msg):
        totalsend = 0
        self.sock.send(bytes([len(msg)]))
        while totalsend < len(msg):
            send = self.sock.send(msg[totalsend:])
            if send == 0:
                raise RuntimeError("socket connection broken while send")
            totalsend += send

    def startingCon(self, ip, port, wlcMsg):
        self.sock.connect((ip, port))
        while self.receive(self).decode() != "Hi":
            self.send(wlcMsg)
        print("connected")

    def waitMSG(self):
        msg = b''
        while msg == b'':
            msg = self.receive()
        msg.decode()
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
    def sendCross(self, int):
        self.sendMSG(str(int))
    

