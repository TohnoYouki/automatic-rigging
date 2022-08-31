import numpy as np
from .huffman import Huffman

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
        self.order = strips[2]

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
        strips, vertices, orders  = [], [], []
        nonvisited = set(range(len(self.triangles)))
        while len(nonvisited) > 0:
            strip = [nonvisited.pop()]
            orders.append([0])
            vertices.append(self.triangles[strip[-1]].tolist())
            edge = self.triangles[strip[-1]][[2, 1]]
            flag = False
            while True:
                neighbours = self.search_triangle(*edge)
                neighbours = [x for x in neighbours if x in nonvisited]
                if len(neighbours) <= 0: break
                strip.append(neighbours[0])
                nonvisited.remove(neighbours[0])
                pick = self.triangles[neighbours[0]]
                i = np.argwhere(pick == edge[0])[0][0]
                orders[-1].append(i)
                vertices[-1].append(pick[(i + 2) % 3])
                if flag: edge = [pick[(i + 2) % 3], pick[(i + 1) % 3]]
                else: edge = [pick[(i + 0) % 3], pick[(i + 2) % 3]]
                flag = not flag
            strips.append(strip)
        return vertices, strips, orders

    @staticmethod
    def __create_triangle__(vindices, tindices, orders):
        number = np.max(np.concatenate(tindices)) + 1
        triangles = np.zeros((number, 3), np.int64)
        for i in range(len(orders)):
            vindex = vindices[i]
            tindex, order = tindices[i], orders[i]
            edge = [vindex[0], vindex[1]]
            for j, index in enumerate(tindex):
                triangles[index] = np.concatenate((edge, [vindex[j + 2]]))
                permute = [(i + 3 - order[j]) % 3 for i in range(3)]
                if j % 2 == 1:
                    edge = [edge[0], vindex[j + 2]]
                else: edge = [vindex[j + 2], edge[1]]
                triangles[index] = triangles[index][permute]
        return triangles

class TriangleCompresser:
    @staticmethod
    def compress(triangles):
        split = {}
        strips = TriangleStrip(triangles.reshape(-1, 3))
        strip_num = len(strips.vertex_strip)
        strips = [[strips.vertex_strip[i], 
                   strips.triangle_strip[i],
                   strips.order[i]] 
                   for i in range(strip_num)]
        strips = sorted(strips, key = lambda x:x[1][0])
        for strip in strips:
            if len(strip[1]) not in split:
                split[len(strip[1])] = []
            split[len(strip[1])].append(strip)
        length = list(sorted(split.keys()))
        strips = sum([split[x] for x in length], [])
        numbers = [len(split[x]) for x in length]
        vindex, tindex, order = \
            map(lambda i:np.concatenate([x[i] for x in strips]), (0, 1, 2))
        tindex = Huffman.compress_diff(tindex)
        vindex = Huffman.compress_diff(vindex)
        order = Huffman.compress(order)
        return {'length': length, 'number': numbers,
                'tindex': tindex, 'vindex': vindex, 'order': order}
    
    @staticmethod
    def decompress(state):
        tcursor, vcursor, strips = 0, 0, []
        tindex = Huffman.decompress_diff(state['tindex'])
        vindex = Huffman.decompress_diff(state['vindex'])
        orders, _ = Huffman.decompress(state['order'])
        for i, length in enumerate(state['length']):
            for _ in range(state['number'][i]):
                triangles = tindex[tcursor:tcursor + length]
                order = orders[tcursor:tcursor + length]  
                vertices = vindex[vcursor:vcursor + length + 2]
                strips.append([vertices, triangles, order])
                tcursor += length
                vcursor += length + 2
        params = list(map(lambda i:[x[i] for x in strips], (0, 1, 2)))
        triangles = TriangleStrip.__create_triangle__(*params)
        return triangles