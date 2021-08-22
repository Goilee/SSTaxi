class hub:
    _initialPos = None

    def __init__(self, TCPobj, pathFinder, parser, mapName) -> None:
        self.TCPobj = TCPobj
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
                    [initialPos, directionVector] = self.TCPobj.getInitialPos()
                else:
                    [initialPos, directionVector] = self._initialPos
                idsOfWay = self.TCPobj.getWay()
                #Shortest path to startpoint
                shortestPath = self.pathFinder(self.pathGraph, initialPos, idsOfWay[0])
                for i in range(len(shortestPath)) - 1:
                    directionFrom = directionVector if i == 0 else self.pathGraph.edges[shortestPath[i - 1], shortestPath[i]]["direction"][1]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1]]["direction"][0]
                    directionTo = [directionTo[0] * -1, directionTo[1] * -1]
                    cosOfVectors = (directionFrom[0] * directionTo[0] + directionFrom[1] * directionTo[1]) / (sqrt(directionFrom[0] ** 2 + directionFrom[1] ** 2) * sqrt(directionTo[0] ** 2 + directionTo[1] ** 2))
                    directionToSend = ""
                    if cosOfVectors < 0:
                        directionToSend = "left"
                    elif cosOfVectors > 0:
                        directionToSend = "right"
                    else:
                        directionToSend = "forward"
                    self.TCPobj.sendDirection(directionToSend)
                
                self._initialPos = [idsOfWay[0], self.pathGraph.edges[shortestPath[-2], shortestPath[-1]]["direction"][1]]
                #Shortest path to destination point
                shortestPath = self.pathFinder(self.pathGraph, idsOfWay[0], idsOfWay[1])
                for i in range(len(shortestPath)) - 1:
                    directionFrom = directionVector if i == 0 else self.pathGraph.edges[shortestPath[i - 1], shortestPath[i]]["direction"][1]
                    directionTo = self.pathGraph.edges[shortestPath[i], shortestPath[i + 1]]["direction"][0]
                    directionTo = [directionTo[0] * -1, directionTo[1] * -1]
                    cosOfVectors = (directionFrom[0] * directionTo[0] + directionFrom[1] * directionTo[1]) / (sqrt(directionFrom[0] ** 2 + directionFrom[1] ** 2) * sqrt(directionTo[0] ** 2 + directionTo[1] ** 2))
                    directionToSend = ""
                    if cosOfVectors < 0:
                        directionToSend = "left"
                    elif cosOfVectors > 0:
                        directionToSend = "right"
                    else:
                        directionToSend = "forward"
                    self.TCPobj.sendDirection(directionToSend)
                self._initialPos = [shortestPath[-1], self.pathGraph.edges[shortestPath[-2], shortestPath[-1]]["direction"][1]]
                self.TCPobj.sendStopSign()
            except KeyboardInterrupt:
                self.TCPobj.close()
                print('Connection closed')
                break