from .TCP import TCP
from socket import SHUT_RDWR
class ClientSocket(TCP):
    def __init__(self,port, wlcMsg, ip):
        super().__init__()
        self.targsock = self.sock
        self.targsock.connect((ip, port))
        self.sendSTR(wlcMsg)
        msg = self.waitSTR()
        if msg != "nihao":
            print("trouble")
        print("connected")

    def sendCross(self, int):
        self.sendINT_List(int)
    def sendPos(self, list):
        self.waitSTR()
        self.sendINT_List(list)


