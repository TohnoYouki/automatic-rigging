import numpy as np
from itertools import accumulate

def calculate_vertex_normal(positions, triangles):
    normal_set = [[] for _ in range(len(positions))]
    triangles = np.array(triangles).reshape(-1, 3)
    for i in range(len(triangles)):
        x, y, z = triangles[i]
        x, y, z = map(lambda x: positions[x], (x, y, z))
        normal = np.cross(y - x, z - x)
        area = np.linalg.norm(normal)
        if np.linalg.norm(normal) < 1e-8:
            normal = [0, 1.0, 0]
        else: normal = normal / np.linalg.norm(normal)
        for j in triangles[i]:
            normal_set[j].append([normal, area])
    normals = np.ones(positions.shape)
    for i in range(len(normal_set)):
        if len(normal_set[i]) <= 0: continue
        normal = [x * weight for x, weight in normal_set[i]]
        normal = np.sum(normal, 0)
        if np.linalg.norm(normal) < 1e-8:
            normal = normal_set[i][0][0]
        if np.linalg.norm(normal) >= 1e-8:
            normals[i] = normal
    normals = normal / np.linalg.norm(normals, axis = 1)[:, np.newaxis]
    return normals

def convert_to_triangle(indices, mode):
    if mode == 0:
        indices = [[x, x, x] for x in indices]
    elif mode == 1:
        assert(len(indices) % 2 == 0)
        line = [[i, i + 1] for i in range(0, len(indices), 2)]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 2:
        line = [[i, (i + 1) % len(indices)] for i in range(len(indices))]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 3:
        line = [[i, i + 1] for i in range(len(indices) - 1)]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 4:
        assert(len(indices) % 3 == 0)
        indices = [[indices[i], indices[i + 1], indices[i + 2]]
                    for i in range(0, len(indices), 3)]
    elif mode == 5:
        assert(len(indices) >= 3)
        indices = [[indices[i], indices[i + 1], indices[i + 2]]
                    if i % 2 == 0 else 
                    [indices[i + 1], indices[i], indices[i + 2]] 
                    for i in range(0, indices - 2)]
    elif mode == 6:
        assert(len(indices) >= 3)
        indices = [[indices[0], indices[i - 1], indices[i]] 
                    for i in range(2, len(indices))]
    else: raise Exception('Unknown Primitive Mode!')
    indices = np.array(indices).reshape(-1)
    return indices

class Geometry:
    def __init__(self, positions, normals, triangles, skins):
        self.vertices = positions
        self.normals = normals
        self.triangles = triangles
        self.skins = skins

    @staticmethod
    def merge_geometries(geometries):
        skins = []
        vertex_num = [len(x.vertices) for x in geometries]
        prefix = list(accumulate([0] + vertex_num))
        vertices = np.concatenate([x.vertices for x in geometries])
        normals = np.concatenate([x.normals for x in geometries])
        triangles = np.concatenate([x.triangles + prefix[i] 
                                    for i, x in enumerate(geometries)])
        for x in geometries: skins.extend(x.skins)
        return Geometry(vertices, normals, triangles, skins)

    def transfer(self, matrix):
        padding = np.ones((len(self.vertices), 1))
        vertices = np.concatenate((self.vertices, padding), 1)
        padding = np.zeros((len(self.normals), 1))
        normals = np.concatenate((self.normals, padding), 1)
        vertices = np.matmul(matrix, vertices.T).T
        normals = np.matmul(np.linalg.inv(matrix).T, normals.T).T
        vertices = vertices[:, :3] / vertices[:, 3:]
        norm = np.linalg.norm(normals, axis = 1)[:, np.newaxis]
        assert(np.min(norm) >= 1e-8)
        normals = normals[:, :3] / norm
        self.vertices, self.normals = vertices, normals

class Primitive:
    def __init__(self, attributes, targets):
        self.names = attributes.keys()
        self.attributes = attributes
        self.targets = targets

    @staticmethod
    def parse_attribute(attributes, accessors):
        result = {}
        if attributes.POSITION is not None:
            result['position'] = accessors[attributes.POSITION]
        if attributes.NORMAL is not None:
            result['normal'] = accessors[attributes.NORMAL]
        if attributes.TANGENT is not None:
            result['tangent'] = accessors[attributes.TANGENT]
        if attributes.TEXCOORD_0 is not None:
            result['texcoord0'] = accessors[attributes.TEXCOORD_0]
        if attributes.TEXCOORD_1 is not None:
            result['texcoord1'] = accessors[attributes.TEXCOORD_1]
        if attributes.COLOR_0 is not None:
            result['color0'] = accessors[attributes.COLOR_0]
        if attributes.JOINTS_0 is not None:
            result['joints0'] = accessors[attributes.JOINTS_0]
        if attributes.WEIGHTS_0 is not None:
            result['weights0'] = accessors[attributes.WEIGHTS_0]
        return result

    @staticmethod
    def parse(primitive, accessors):
        attributes = primitive.attributes
        attributes = Primitive.parse_attribute(attributes, accessors)
        targets = [Primitive.parse_attribute(x, accessors) 
                   for x in primitive.targets]
        indices = accessors[primitive.indices].reshape(-1)
        indices = convert_to_triangle(indices, primitive.mode)
        attributes['triangle'] = indices
        assert('position' in attributes)
        if 'normal' not in attributes:
            params = (attributes['position'], indices)
            attributes['normal'] = calculate_vertex_normal(*params)
        return Primitive(attributes, targets)

    def get_attribute(self, weights):
        assert(len(weights) == len(self.targets))
        result = {}
        for name in self.names:
            result[name] = self.attributes[name].copy()
            for i, weight in enumerate(weights):
                if name not in self.targets[i]: continue
                result[name] += weight * self.targets[i][name]
        return result

    def get_skin_geometry(self, weights):
        attributes = self.get_attribute(weights)
        vertices = attributes['position']
        normals = attributes['normal']
        triangles = attributes['triangle']
        if 'joints0' in attributes and 'weights0' in attributes:
            joints = attributes['joints0']
            weights = attributes['weights0']
            assert(joints.shape == weights.shape)
            assert(len(joints.shape) == 2)
            assert(np.max(np.abs(np.sum(weights, 1) - 1.0)) < 1e-5)
            skins = [[[joints[i][j], weights[i][j]] 
                 for j in range(len(joints[i]))] for i in range(len(joints))]
        else: skins = [[] for _ in range(len(vertices))]
        assert(len(vertices) == len(skins))
        assert(len(normals) == len(skins))
        return Geometry(vertices, normals, triangles, skins)

class Mesh:
    def __init__(self, name, primitives, default_weights):
        self.name = name
        self.primitives = primitives
        self.default_weights = default_weights

    @staticmethod
    def parse(mesh, accessors):
        primitives = [Primitive.parse(x, accessors) 
                      for x in mesh.primitives]
        return Mesh(mesh.name, primitives, mesh.weights)

    def get_mesh(self, matrix = np.identity(4), weights = None):
        if weights is None:
            weights = self.default_weights
        geometries = [x.get_skin_geometry(weights) 
                      for x in self.primitives]
        mesh = Geometry.merge_geometries(geometries)
        mesh.transfer(matrix)
        return mesh

def parse_mesh(gltf, accessors):
    return [Mesh.parse(x, accessors) for x in gltf.meshes]