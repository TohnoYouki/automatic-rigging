import numpy as np

class TriangleStrip:
    def __init__(self, triangles):
        self.triangles = triangles
        self.incident = {}
        for i in range(len(triangles)):
            for v in triangles[i]: 
                if v not in self.incident: 
                    self.incident[v] = []
                self.incident[v].append(i)
        strips = self.__create_triangle_strip__()
        self.vertex_strip = strips[0]
        self.triangle_strip = strips[1]

    def search_triangle(self, x, y):
        result = []
        incidient = set(self.incident[x] + self.incident[y])
        for i in incidient:
            triangle = self.triangles[i]
            for j in range(3):
                if triangle[j] == x and triangle[(j + 1) % 3] == y:
                    result.append(i)
        result = list(set(result))
        return result

    def __create_triangle_strip__(self):
        strips, vertices  = [], []
        nonvisited = set(range(len(self.triangles)))
        while len(nonvisited) > 0:
            strip = [nonvisited.pop()]
            vertices.append(self.triangles[strip[-1]].tolist())
            edge = self.triangles[strip[-1]][[2, 1]]
            flag = True
            while True:
                neighbours = self.search_triangle(*edge)
                neighbours = [x for x in neighbours if x in nonvisited]
                if len(neighbours) <= 0: break
                strip.append(neighbours[0])
                nonvisited.remove(neighbours[0])
                pick = self.triangles[neighbours[0]]
                i = np.argwhere(pick == edge[0])[0][0]
                vertices[-1].append(pick[(i + 2) % 3])
                if flag: edge = [pick[(i + 2) % 3], pick[(i + 1) % 3]]
                else: edge = [pick[(i + 0) % 3], pick[(i + 2) % 3]]
                flag = not flag
            strips.append(strip)
        return vertices, strips