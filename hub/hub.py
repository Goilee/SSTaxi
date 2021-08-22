from mapParser.parser import parseYAML2GRAPH
from pathFinder.bfs import bfs
from TCP.TCPServer import ServerSocket

class hub:
    _initialPos = None

    def __init__(self, TCPobjR, TCPobjUI, pathFinder, parser, mapName) -> None:
        self.TCPobjR = TCPobjR
        self.TCPobjUI = TCPobjUI
        self.pathFinder = pathFinder
        print('Start parsing')
        self.pathGraph = parser(mapName)
        print('Parsing is done')

    def actionLoop(self):
        from math import sqrt
        while True:
            initialPos = None
            try:
                if self._initialPos == None:
                    [initialPos, directionVector] = self.TCPobjR.getInitialPos()
                else:
                    [initialPos, directionVector] = self._initialPos
                idsOfWay = self.TCPobjUI.getWay()
                #Shortest path to startpoint
                shortestPath = self.pathFinder(self.pathGraph, initialPos, idsOfWay[0])
                for i in range(len(shortestPath)) - 1:
                    directionFrom = directionVector if i == 0 else self.pathGraph.edges[shortestPath[i - 1], shortestPath[i]]["direction"][1 if shortestPath[i] < shortestPath[i + 1] else 0]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1]]["direction"][0 if shortestPath[i] < shortestPath[i + 1] else 1]
                    directionTo = [directionTo[0] * -1, directionTo[1] * -1]
                    cosOfVectors = (directionFrom[0] * directionTo[0] + directionFrom[1] * directionTo[1]) / (sqrt(directionFrom[0] ** 2 + directionFrom[1] ** 2) * sqrt(directionTo[0] ** 2 + directionTo[1] ** 2))
                    directionToSend = ""
                    if cosOfVectors < 0:
                        directionToSend = "left"
                    elif cosOfVectors > 0:
                        directionToSend = "right"
                    else:
                        directionToSend = "forward"
                    self.TCPobjR.sendDirection(directionToSend)
                
                self._initialPos = [idsOfWay[0], self.pathGraph.edges[shortestPath[-2], shortestPath[-1]]["direction"][1]]
                #Shortest path to destination point
                shortestPath = self.pathFinder(self.pathGraph, idsOfWay[0], idsOfWay[1])
                for i in range(len(shortestPath)) - 1:
                    directionFrom = directionVector if i == 0 else self.pathGraph.edges[shortestPath[i - 1], shortestPath[i]]["direction"][1 if shortestPath[i] < shortestPath[i + 1] else 0]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1]]["direction"][0 if shortestPath[i] < shortestPath[i + 1] else 1]
                    directionTo = [directionTo[0] * -1, directionTo[1] * -1]
                    cosOfVectors = (directionFrom[0] * directionTo[0] + directionFrom[1] * directionTo[1]) / (sqrt(directionFrom[0] ** 2 + directionFrom[1] ** 2) * sqrt(directionTo[0] ** 2 + directionTo[1] ** 2))
                    directionToSend = ""
                    if cosOfVectors < 0:
                        directionToSend = "left"
                    elif cosOfVectors > 0:
                        directionToSend = "right"
                    else:
                        directionToSend = "forward"
                    self.TCPobjR.sendDirection(directionToSend)
                self._initialPos = [shortestPath[-1], self.pathGraph.edges[shortestPath[-2], shortestPath[-1]]["direction"][1]]
                self.TCPobjUI.sendStopSign()
            except KeyboardInterrupt:
                self.TCPobjR.close()
                self.TCPobjUI.close()
                print('Connection closed')
                break

sSocketR = ServerSocket(2222)
sSocketR.waitCon("Hello Robot")

sSocketUI = ServerSocket(3333)
sSocketUI.waitCon("Hello UI")

h = hub(sSocketR, sSocketUI, bfs, parseYAML2GRAPH, '../map.yaml')