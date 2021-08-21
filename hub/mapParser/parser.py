from typing import List
from networkx.algorithms.shortest_paths import weighted
import yaml
import networkx as nx

def parseYAML2GRAPH(filename: str) -> nx.Graph:
    tiles = {}
    with open(filename, 'r') as stream:
        try:
            tiles = yaml.safe_load(stream)["tiles"]
        except yaml.YAMLError as exc:
            print(exc)

    def decodeSide(side) -> List[int]:
        if side == 'W':
            return [0, -1]
        elif side == 'E':
            return [0, 1]
        elif side == 'N':
            return [-1, 0]
        elif side == 'S':
            return [1, 0]

    def findFstCross(tilesForFunc) -> List[int]:
        for rowId, row in enumerate(tilesForFunc):
            for colId, col in enumerate(row):
                if col[:-2] in ['3way_left', '3way_right', '4way'] or col == '4way':
                    return [rowId, colId]

    def updateCrosses(tilesForFunc):
        count = 0
        for rowId, row in enumerate(tilesForFunc):
            for colId, col in enumerate(row):
                if col[:-2] in ['3way_left', '3way_right'] or col == '4way':
                    tilesForFunc[rowId][colId] = [col, count]
                    count += 1
        return tilesForFunc

    def rotateRight(dcoords):
        if dcoords[0] == 0 and dcoords[1] == 1:
            return [1, 0]
        elif dcoords[0] == 0 and dcoords[1] == -1:
            return [-1, 0]
        elif dcoords[0] == 1 and dcoords[1] == 0:
            return [0, -1]
        elif dcoords[0] == -1 and dcoords[1] == 0:
            return [0, 1]

    def follow(startCoords, dCoords, count = 0):
        coords = [startCoords[0] + dCoords[0], startCoords[1] + dCoords[1]]
        if type(tiles[coords[0]][coords[1]]) is list and (tiles[coords[0]][coords[1]][0][:-2] in ['3way_left', '3way_right'] or tiles[coords[0]][coords[1]][0] == '4way'):
            dCoords = [dCoords[1] * -1, dCoords[0] * -1]
            return [coords, count, dCoords]
        side = tiles[coords[0]][coords[1]][-1]
        item = tiles[coords[0]][coords[1]][:-2]
        tiles[coords[0]][coords[1]] = -1
        if item == 'straight':
            if startCoords[1] - coords[1] == -1:
                return follow(coords, [0, 1], count + 1)
            elif startCoords[1] - coords[1] == 1:
                return follow(coords, [0, -1], count + 1)
            elif startCoords[0] - coords[0] == -1:
                return follow(coords, [1, 0], count + 1)
            elif startCoords[0] - coords[0] == 1:
                return follow(coords, [-1, 0], count + 1)
        if item in ['curve_left', 'curve_right']:
            return follow(coords, rotateRight(rotateRight(decodeSide(side))), count + 1)
            

    def parse(crossCoords, graph):
        if tiles[crossCoords[0]][crossCoords[1]][0] == '4way':
            dCoords = [1, 0]
            for i in range(4):
                dCoords = rotateRight(dCoords)
                if tiles[crossCoords[0] + dCoords[0]][crossCoords[1] + dCoords[1]] != -1:
                    [coords, length, direction] = follow(crossCoords, dCoords)
                    graph.add_edge(tiles[crossCoords[0]][crossCoords[1]][1], tiles[coords[0]][coords[1]][1], weight = length, direction = [[dCoords[1], dCoords[0]], direction])
                    parse(coords, graph)
        elif tiles[crossCoords[0]][crossCoords[1]][0][:-2] == '3way_left':
            dCoords = decodeSide(tiles[crossCoords[0]][crossCoords[1]][0][-1])
            dCoords = rotateRight(dCoords)
            for i in range(3):
                dCoords = rotateRight(dCoords)
                if tiles[crossCoords[0] + dCoords[0]][crossCoords[1] + dCoords[1]] != -1:
                    [coords, length, direction] = follow(crossCoords, dCoords)
                    graph.add_edge(tiles[crossCoords[0]][crossCoords[1]][1], tiles[coords[0]][coords[1]][1], weight = length, direction = [[dCoords[1], dCoords[0]], direction])
                    parse(coords, graph)
        elif tiles[crossCoords[0]][crossCoords[1]][0][:-2] == '3way_right':
            dCoords = decodeSide(tiles[crossCoords[0]][crossCoords[1]][0][-1])
            for i in range(3):
                if tiles[crossCoords[0] + dCoords[0]][crossCoords[1] + dCoords[1]] != -1:
                    [coords, length, direction] = follow(crossCoords, dCoords)
                    graph.add_edge(tiles[crossCoords[0]][crossCoords[1]][1], tiles[coords[0]][coords[1]][1], weight = length, direction = [[dCoords[1], dCoords[0]], direction])
                    parse(coords, graph)
                dCoords = rotateRight(dCoords)
    
    origin = nx.MultiGraph()
    origin.add_node(0)
    fstCross = findFstCross(tiles)
    tiles = updateCrosses(tiles)
    parse(fstCross, origin)
    return origin