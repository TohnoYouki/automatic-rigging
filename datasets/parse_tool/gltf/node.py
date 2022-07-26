import numpy as np
from scipy.spatial.transform.rotation import Rotation as R

def transformation_matrix(translation, rotation, scale):
    scale_matrix = np.identity(4)
    translation_matrix = np.identity(4)
    for i in range(3): 
        scale_matrix[i, i] = scale[i]
        translation_matrix[i, 3] = translation[i]
    rotation_matrix = np.identity(4)
    rotation_matrix[:3, :3] = R.from_quat(rotation).as_matrix()
    matrix = np.matmul(rotation_matrix, scale_matrix)
    matrix = np.matmul(translation_matrix, matrix)
    return matrix

class Node:
    def __init__(self, name, skeleton, weights, local_matrix, mesh):
        self.name = name
        self.weights = weights
        self.skeleton_index = skeleton
        self.local_matrix = local_matrix
        self.global_matrix = None
        self.parent = None
        self.children = []
        self.mesh = mesh

    @staticmethod
    def parse_matrix(node):
        params = [node.translation, node.rotation, node.scale]
        default = [[0, 0, 0], [0, 0, 0, 1], [1, 1, 1]]
        node_matrix = node.matrix
        if node_matrix is not None:
            node_matrix = np.array(node_matrix).reshape(4, 4)
            node_matrix = node_matrix.transpose(1, 0)
        if params.count(None) != 3 or node_matrix is None:
            params = [x if x is not None else default[i] 
                      for i, x in enumerate(params)]
            matrix = transformation_matrix(*params)
            if node_matrix is not None:
                diff = node_matrix - matrix.reshape(-1)
                assert(np.linalg.norm(diff) <= 1e-8)
                matrix = node_matrix
        else: matrix = node_matrix
        return matrix

    @staticmethod
    def parse(node, meshes):
        local_matrix = Node.parse_matrix(node)
        if node.mesh is not None:
            mesh = meshes[node.mesh]
        else: mesh = None
        if hasattr(node, 'weights'):
            weights = node.weights
        else: weights = None
        return Node(node.name, node.skin, weights, local_matrix, mesh)

    def global_position(self):
        coord = self.global_matrix[:, 3]
        return coord[:3] / coord[3]

    def global_mesh(self):
        if self.mesh is None: return None
        return self.mesh.get_mesh(self.global_matrix, self.weights)

    def node_set(self):
        result = []
        for child in self.children:
            nodes = [x for x in child.node_set() if x not in result]
            result.extend(nodes)
        result.append(self)
        return result

def parse_node(gltf, meshes):
    nodes = [Node.parse(x, meshes) for x in gltf.nodes]
    for i in range(len(nodes)):
        children = set(gltf.nodes[i].children)
        for child in children:
            nodes[i].children.append(nodes[child])
            assert(nodes[child].parent is None)
            nodes[child].parent = nodes[i]
    while True:
        change = False
        for i in range(len(nodes)):
            if nodes[i].global_matrix is not None: continue
            if nodes[i].parent is None: 
                nodes[i].global_matrix = nodes[i].local_matrix.copy()
                change = True
            elif nodes[i].parent.global_matrix is not None:
                parent_matrix = nodes[i].parent.global_matrix
                local_matrix = nodes[i].local_matrix
                nodes[i].global_matrix = np.matmul(parent_matrix, local_matrix)
                change = True
        if not change: break
    assert(all([x.global_matrix is not None for x in nodes]))
    return nodes