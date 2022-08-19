from .mesh import Mesh
from .skeleton import Skeleton

class Rigging:
    def __init__(self, mesh, skeleton, skins):
        self.mesh = mesh
        self.skeleton = skeleton
        self.skin = skins
        assert(isinstance(self.mesh, Mesh))
        assert(isinstance(self.skeleton, Skeleton))
        assert(len(self.skin) == len(self.mesh.vertices) // 3)
        assert(all([all([i >= 0 and i < len(self.skeleton.names) 
                 for i, w in x]) for x in self.skin]))

    @staticmethod
    def create(vertices, normals, triangles, names, positions, parents, skins):
        mesh = Mesh(vertices, normals, triangles)
        skeleton = Skeleton(names, positions, parents)
        return Rigging(mesh, skeleton, skins)