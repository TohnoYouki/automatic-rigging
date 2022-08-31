import numpy as np
from .skin import Skin
from .mesh import Mesh

class Rigging:
    def __init__(self, mesh, skeleton_id, skins):
        self.mesh = mesh
        self.skeleton = skeleton_id
        self.skin = skins
        assert(isinstance(self.mesh, Mesh))
        assert(isinstance(self.skin, Skin))
        assert(len(self.skin.numbers) == len(self.mesh.vertices))

    def state_dict(self):
        return {'mesh': self.mesh.state_dict(),
                'skeleton_id': self.skeleton,
                'skin': self.skin.state_dict()}

    @staticmethod
    def load_state_dict(state):
        mesh = Mesh.load_state_dict(state['mesh'])
        skeleton = state['skeleton_id']
        skin = Skin.load_state_dict(state['skin'])
        return Rigging(mesh, skeleton, skin)

    def skin_mesh(self, joint_matrixs, global_matrix = np.identity(4)):
        skins = self.skin.vertex_skins()
        if self.skeleton is not None:
            ib_matrixs = self.skin.inverse_bind_matrixs
            joint_matrixs = np.matmul(joint_matrixs, ib_matrixs)
            vertices_matrixs = []
            for i in range(len(skins)):
                if len(skins[i]) > 0:
                    matrixs = [joint_matrixs[j] * w for j, w in skins[i]]
                    vertices_matrixs.append(np.sum(matrixs, axis = 0))
                else: vertices_matrixs.append(global_matrix)
            matrixs = np.array(vertices_matrixs)
            mesh = self.mesh.transfer(matrixs)
        else: mesh = self.mesh.transfer(global_matrix)
        return Rigging(mesh, self.skeleton, self.skin)