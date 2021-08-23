from math import floor
from mapParser.parser import parseYAML2GRAPH
from pathFinder.bfs import bfs
from SSTaxi.TCP.TCPServer import ServerSocket
import socket

class hub:
    _initialPos = None

    def __init__(self, TCPobjR: ServerSocket, TCPobjUI: ServerSocket, pathFinder, parser, mapName) -> None:
        self.TCPobjR = TCPobjR
        self.TCPobjUI = TCPobjUI
        self.pathFinder = pathFinder
        print('Start parsing')
        self.pathGraph = parser(mapName)
        print('Parsing is done')

    def actionLoop(self):
        def convertFromStrToVector(fvar):
            fvar = floor(fvar * 10) / 10
            print(fvar)
            if fvar in [-1.0, -0.9, -0.8, 0.9, 0.8, 1.0]:
                return [-1, 0]
            elif fvar in [-0.0, -0.1, -0.2, 0.0, 0.1, 0.2]:
                return [1, 0]
            elif fvar in [0.5, 0.4, 0.3, 0.6, 0.7]:
                return [0, 1]
            elif fvar in [-0.5, -0.4, -0.3, -0.6, -0.7]:
                return [0, -1]
        def rotateRight(vec):
            return [vec[1], vec[0] * -1]
        self.TCPobjR.waitCon('taxi')
        while True:
            try:
                if self._initialPos == None:
                    [initialPos, directionVector] = self.TCPobjR.getCrossList()
                    self.TCPobjUI.waitCon('banana')
                    directionVector = convertFromStrToVector(directionVector)
                    self._initialPos = [initialPos, directionVector]
                else:
                    [initialPos, directionVector] = self._initialPos
                print('initial pos', self._initialPos)
                idsOfWay = self.TCPobjUI.getWay()
                #Shortest path to startpoint
                print(idsOfWay, 'way')
                shortestPath = self.pathFinder(self.pathGraph, initialPos, idsOfWay[0])
                for i in range(len(shortestPath) - 1):
                    directionFrom = self._initialPos[1]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1], 0]["direction"][0 if shortestPath[i] < shortestPath[i + 1] else 1]
                    print('from', directionFrom, 'to', directionTo)
                    newDirection = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1], 0]["direction"][1 if shortestPath[i] < shortestPath[i + 1] else 0]
                    self._initialPos = [shortestPath[i + 1], [newDirection[0] * -1, newDirection[1] * -1]]
                    directionToSend = ""
                    forward = directionFrom
                    right = rotateRight(directionFrom)
                    left = rotateRight(rotateRight(rotateRight(directionFrom)))
                    if left[0] == directionTo[0] and left[1] == directionTo[1]:
                        directionToSend = "left"
                    elif right[0] == directionTo[0] and right[1] == directionTo[1]:
                        directionToSend = "right"
                    elif forward[0] == directionTo[0] and forward[1] == directionTo[1]:
                        directionToSend = "crossroad"
                    else:
                        directionToSend = "turnover"
                    print(directionToSend, self._initialPos)
                    self.TCPobjR.waitSTR()
                    self.TCPobjR.sendDirection(directionToSend)
                    self.TCPobjUI.sendINT(shortestPath[i] + 1)
                    self.TCPobjR.getCrossId()
                
                #Shortest path to destination point
                shortestPath = self.pathFinder(self.pathGraph, idsOfWay[0], idsOfWay[1])
                for i in range(len(shortestPath) - 1):
                    directionFrom = self._initialPos[1]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1], 0]["direction"][0 if shortestPath[i] < shortestPath[i + 1] else 1]
                    print('from', directionFrom, 'to', directionTo)
                    newDirection = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1], 0]["direction"][1 if shortestPath[i] < shortestPath[i + 1] else 0]
                    self._initialPos = [shortestPath[i + 1], [newDirection[0] * -1, newDirection[1] * -1]]
                    directionToSend = ""
                    forward = directionFrom
                    right = rotateRight(directionFrom)
                    left = rotateRight(rotateRight(rotateRight(directionFrom)))
                    if left[0] == directionTo[0] and left[1] == directionTo[1]:
                        directionToSend = "left"
                    elif right[0] == directionTo[0] and right[1] == directionTo[1]:
                        directionToSend = "right"
                    elif forward[0] == directionTo[0] and forward[1] == directionTo[1]:
                        directionToSend = "crossroad"
                    else:
                        directionToSend = "turnover"
                    print(directionToSend, self._initialPos)
                    self.TCPobjR.waitSTR()
                    self.TCPobjR.sendDirection(directionToSend)
                    self.TCPobjUI.sendINT(shortestPath[i] + 1)
                    self.TCPobjR.getCrossId()
                self.TCPobjUI.sendStopSign()
            except KeyboardInterrupt:
                self.TCPobjR.close()
                self.TCPobjUI.close()
                print('Connection closed')
                break


class test:
    def __init__(self) -> None:
        pass

    def getInitialPos(self):
        id = int(input('id - '))
        dir = input('dir float - ')
        return [id, dir]
    
    def sendDirection(self, dir):
        print(dir)

    def getWay(self):
        start = int(input('start - '))
        stop = int(input('stop - '))
        return [start, stop]

hostIp = '192.168.189.26'
print('ip -', hostIp)

sSocketUI = ServerSocket(25566, hostIp)
sSocketR = ServerSocket(25565, hostIp)

h = hub(sSocketR, sSocketUI, bfs, parseYAML2GRAPH, '../map.yaml')
h.actionLoop()
