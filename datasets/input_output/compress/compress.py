import numpy as np
from ..basic import *

def unit_vectors_to_oct(vectors):
    denominator = np.sum(np.abs(vectors), axis = 1)
    result = (vectors[:, :2] / denominator[:, None]).copy()
    negative = vectors[:, 2] <= 0.0
    sign = -np.ones(result.shape)
    sign[result >= 0.0] = 1.0
    result[negative] = 1.0 - np.abs(result[negative])[:, [1, 0]]
    result[negative] *= sign[negative]
    return result

def oct_to_unit_vectors(vectors):
    z = 1.0 - np.abs(vectors[:, 0]) - np.abs(vectors[:, 1])
    result = np.concatenate((vectors[:, :2], z[:, None]), axis = 1)
    negative = z < 0
    sign = -np.ones((len(result), 2))
    sign[result[:, :2] >= 0.0] = 1.0
    result[negative, :2] = 1.0 - np.abs(result[negative][:, [1, 0]])
    result[negative, :2] *= sign[negative]
    result = result / np.linalg.norm(result, axis = 1)[:, None]
    return result

class Compresser:
    @staticmethod
    def compress_skeleton(names, positions, parents):
        result = {'joint name': names, 'joint parent': parents,
                  'joint position': positions.reshape(-1, 3)}
        return result

    @staticmethod
    def decompress_skeleton(dicts):
        names = dicts['joint name']
        parents = dicts['joint parent']
        positions = dicts['joint position'].reshape(-1)
        return names, positions, parents

    @staticmethod
    def compress_mesh(vertices, normals, triangles):
        vertices = vertices.reshape(-1, 3)
        normals = normals.reshape(-1, 3)
        octs = unit_vectors_to_oct(normals)
        triangles = triangles.reshape(-1, 3)
        if np.max(triangles) < 65536:
            triangles = triangles.astype(np.uint16)
        else: triangles = triangles.astype(np.uint32)
        result = {'mesh vertex': vertices, 'mesh normal': octs,
                  'mesh triangle': triangles}
        return result

    @staticmethod
    def decompress_mesh(dicts):
        vertices = dicts['mesh vertex'].reshape(-1)
        octs = dicts['mesh normal'].reshape(-1, 2)
        normals = oct_to_unit_vectors(octs).reshape(-1)
        triangles = dicts['mesh triangle'].reshape(-1)
        triangles = triangles.astype(np.int64)
        return vertices, normals, triangles

    @staticmethod
    def compress_skin(skins):
        numbers, flags, indices, weights = [], [], [], []
        for skin in skins:
            numbers.append(len(skin))
            if len(skin) == 0: continue
            sum_one = np.abs(np.sum([w for _, w in skin]) - 1.0) < 1e-10
            for i, w in skin:
                indices.append(i)
                if w != 0 and sum_one:
                    flags.append(2)
                    sum_one = False
                elif w != 0:
                    flags.append(1)
                    weights.append(w)
                else: flags.append(0)
        flags = np.array(flags).astype(np.int8)
        if np.max(numbers) < 128:
            numbers = np.array(numbers).astype(np.int8)
        else: numbers = np.array(numbers).astype(np.int16)
        if np.max(indices) < 256:
            indices = np.array(indices).astype(np.uint8)
        else: indices = np.array(indices).astype(np.uint16)
        weights = np.array(weights)
        return {'skin number': numbers, 'skin index': indices, 
                'skin weight': weights, 'skin flag': flags}

    @staticmethod
    def decompress_skin(dicts):
        skins, index, windex = [], 0, 0
        numbers, indices = dicts['skin number'], dicts['skin index']
        weights, flags = dicts['skin weight'], dicts['skin flag']
        for number in numbers:
            skins.append([])
            for _ in range(number):
                if flags[index] == 0:
                    skins[-1].append([indices[index], 0])
                elif flags[index] == 1:
                    skins[-1].append([indices[index], weights[windex]])
                    windex += 1
                else: skins[-1].append([indices[index], None])
                index += 1
            values = [x[1] for x in skins[-1]]
            if values.count(None) == 1:
                i = values.index(None)
                residual = np.sum([x for x in values if x is not None])
                skins[-1][i][1] = 1.0 - residual
        return skins

    @staticmethod
    def compress(rigging):
        mesh = rigging.mesh
        mesh = (mesh.vertices, mesh.normals, mesh.triangles)
        result = Compresser.compress_mesh(*mesh)
        skeleton = rigging.skeleton
        skeleton = (skeleton.names, skeleton.positions, skeleton.parents)
        result.update(Compresser.compress_skeleton(*skeleton))
        result.update(Compresser.compress_skin(rigging.skin))
        return result

    @staticmethod
    def decompress(datas):
        vertices, normals, triangles = Compresser.decompress_mesh(datas)
        mesh = Mesh(vertices, normals, triangles)
        names, positions, parents = Compresser.decompress_skeleton(datas)
        skeleton = Skeleton(names, positions, parents)
        skins = Compresser.decompress_skin(datas)
        return Rigging(mesh, skeleton, skins)