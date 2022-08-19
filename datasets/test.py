import numpy as np
from input_output.basic import *
from input_output.convert import Converter

class StripCompresser: 
    @staticmethod
    def extract_triangle_strip(triangles):
        split = {}
        strips = TriangleStrip(triangles)
        strip_num = len(strips.vertex_strip)
        strips = [[strips.vertex_strip[i], strips.triangle_strip[i]] 
                   for i in range(strip_num)]
        strips = sorted(strips, key = lambda x:x[1][0])
        for strip in strips:
            if len(strip[1]) not in split:
                split[len(strip[1])] = []
            split[len(strip[1])].append(strip)
        length = list(sorted(split.keys()))
        strips = sum([split[x] for x in length], [])
        return strips

    @staticmethod
    def compress_positions(positions, strips):
        positions = np.array(positions).reshape(-1, 3)
        strips = [x[0] for x in strips]
        flag = np.zeros(len(positions), dtype = np.bool_)
        #numbers = []
        test = {i:0 for i in range(256)}
        for i, strip in enumerate(strips):
            for j, vertex in enumerate(strip):
                if flag[vertex]: continue
                flag[vertex] = True
                if j > 3:
                    x, y, z = map(lambda x:positions[strip[j - x]], [1, 2, 3])
                    predict = x + y - z
                elif j > 0: predict = positions[strip[j - 1]]
                elif i > 0: predict = positions[strips[i - 1][0]]
                else: predict = np.zeros(3)
                predict = np.array(predict, dtype = positions.dtype)
                predict = predict.tobytes()
                position = positions[vertex].tobytes()
                position = np.frombuffer(position, np.uint8).reshape(3, 8)
                predict = np.frombuffer(predict, np.uint8).reshape(3, 8)
                diff = np.bitwise_xor(position, predict)
                for x in diff.reshape(-1):
                    test[x] += 1
        print(test, len(positions) * 3 * 8 / 256)
                #number = 0
                #for i in range(3):
                #    for j in range(8):
                #        if diff[i][7 - j] == 0: number += 1
                #        else: break
                #numbers.append(number)                
        #print(len(numbers), np.mean(numbers))


    @staticmethod
    def compress(rigging):
        mesh = rigging.mesh
        triangles = mesh.triangles.reshape(-1, 3)
        strips = StripCompresser.extract_triangle_strip(triangles)
        StripCompresser.compress_positions(mesh.vertices, strips)

        #number = {x:len(split[x]) for x in split}
        #length = list(sorted(number.keys()))
        #number = [number[x] for x in length]
        #strips = sum([split[x] for x in length], [])
        #tindex = np.concatenate([x[1] for x in strips])
        #vindex = np.concatenate([x[0] for x in strips])        
        #return number, length, tindex, vindex

test = Converter.convert('/home/tohnoyouki/Desktop/left/9a7eae7771f94572aa72ca153153f340.glb')
StripCompresser.compress(test[0])