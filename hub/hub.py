class hub:
    _initialPos = None

    def __init__(self, TCPobj, pathFinder, parser, mapName) -> None:
        self.TCPobj = TCPobj
        self.pathFinder = pathFinder
        print('Start parsing')
        self.pathGraph = parser(mapName)
        print('Parsing is done')

    def actionLoop(self):
        while True:
            initialPos = None
            try:
                if self._initialPos == None:
                    initialPos = self.TCPobj.getInitialPos()
                else:
                    initialPos = self._initialPos
                idsOfWay = self.TCPobj.getWay()
                #Shortest path to initial point
                shortestPath = self.pathFinder(self.pathGraph, initialPos, idsOfWay[0])
                for i in shortestPath:
                    pass
                #Shortest path to destination point
                shortestPath = self.pathFinder(self.pathGraph, idsOfWay[0], idsOfWay[1])
                for i in shortestPath:
                    pass
                self.TCPobj.sendStopSign()
            except KeyboardInterrupt:
                self.TCPobj.close()
                print('Connection closed')
                break
                
        
        