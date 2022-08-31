import numpy as np
from itertools import accumulate
from .utils import calculate_vertex_normal, convert_to_triangle

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

class Primitive:
    def __init__(self, attributes, targets):
        self.names = attributes.keys()
        self.attributes = attributes
        self.targets = targets

    @staticmethod
    def parse_attribute(attributes, accessors):
        result = {}
        keys = {'POSITION': 'position', 'NORMAL':'normal', 'TANGENT': 'tangent', 
                'TEXCOORD_0': 'texcoord0', 'TEXCOORD_1': 'texcoord1', 
                'COLOR_0': 'color0', 'JOINTS_0': 'joints0', 'WEIGHTS_0': 'weights0'}
        if isinstance(attributes, dict):
            for key, index in attributes.items():
                assert(key in keys)
                result[keys[key]] = accessors[index]
            return result
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
        weights, result = np.array(weights), {}
        for name in self.names:
            result[name] = self.attributes[name].copy()
            morph = [[weight, target[name]] for weight, target 
                      in zip(weights, self.targets) if name in target]
            if len(morph) == 0: continue
            shape = morph[0][1].shape
            morph_weights = np.array([x[0] for x in morph])[None]
            morph_targets = np.concatenate([x[1].reshape(1, -1) for x in morph])
            morph = np.matmul(morph_weights, morph_targets)[0].reshape(shape)
            if name == 'tangent' and result[name].shape[1] == 4:
                tangent = result[name][:, :3] + morph[:, :3]
                tangent = np.concatenate((tangent, result[name][:, 3:]), axis = 1)
                result[name] = tangent
            else: result[name] = morph + result[name]
        return result

    def get_skin_geometry(self, weights):
        attributes = self.get_attribute(weights)
        vertices = attributes['position']
        normals = attributes['normal']
        triangles = attributes['triangle']
        assert(len(vertices) == len(normals))
        if 'joints0' in attributes and 'weights0' in attributes:
            joints = attributes['joints0']
            weights = attributes['weights0']
            assert(joints.shape == weights.shape)
            assert(len(joints.shape) == 2)
            assert(len(vertices) == len(joints))
        else: joints, weights = None, None
        skins = [[] for _ in range(len(vertices))]
        if joints is not None:
            for i in range(len(joints)):
                for j in range(len(joints[i])):
                    skins[i].append([joints[i][j], weights[i][j]])
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

    def mesh(self, weights = None):
        if weights is None:
            weights = self.default_weights
        geometries = [x.get_skin_geometry(weights) 
                      for x in self.primitives]
        mesh = Geometry.merge_geometries(geometries)
        return mesh

def parse_mesh(gltf, accessors):
    return [Mesh.parse(x, accessors) for x in gltf.meshes]