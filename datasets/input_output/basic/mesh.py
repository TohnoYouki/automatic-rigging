import numpy as np

class Mesh:
    def __init__(self, vertices, normals, triangles):
        self.vertices = vertices
        self.normals = normals
        self.triangles = triangles
        assert(len(vertices) == len(normals))
        assert(np.min(triangles) >= 0)
        assert(np.max(triangles)) < len(vertices)

    def state_dict(self):
        state = {}
        state['vertex'] = self.vertices
        state['normal'] = self.normals
        state['triangle'] = self.triangles
        return state

    @staticmethod
    def load_state_dict(state):
        vertices = state['vertex']
        normals = state['normal']
        triangles = state['triangle']
        return Mesh(vertices, normals, triangles)

    @staticmethod
    def normal_matrix(matrix):
        matrix = matrix.copy()
        matrix[..., :3, 3] = 0
        matrix = np.linalg.pinv(matrix)
        shape = [i for i in range(len(matrix.shape))]
        shape[-1], shape[-2] = len(shape) - 2, len(shape) - 1
        matrix = matrix.transpose(*shape)
        return matrix

    def transfer(self, matrix):
        padding = np.ones((len(self.vertices), 1))
        vertices = np.concatenate((self.vertices, padding), 1)
        vertices = vertices.reshape(-1, 4, 1)
        padding = np.zeros((len(self.normals), 1))
        normals = np.concatenate((self.normals, padding), 1)
        normals = normals.reshape(-1, 4, 1)
        vertices = np.matmul(matrix, vertices)[:, :, 0]
        normal_matrix = Mesh.normal_matrix(matrix)
        normals = np.matmul(normal_matrix, normals)[:, :, 0]
        vertices = vertices[:, :3] / vertices[:, 3:]
        assert(np.max(np.abs(normals[:, 3:])) < 1e-5)
        normals = normals[:, :3]
        zero = np.linalg.norm(normals, axis = 1) <= 1e-8
        normals[zero] = np.ones((np.sum(zero), 3))
        norm = np.linalg.norm(normals, axis = 1)[:, np.newaxis]
        assert(np.min(norm) >= 1e-8)
        normals = normals / norm
        return Mesh(vertices, normals, self.triangles)