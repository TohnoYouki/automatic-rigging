import os
import numpy as np
from .mesh import Mesh
from .skin import Skin
from .rigging import Rigging
from .skeleton import Skeleton
from itertools import accumulate

class Scene:
    def __init__(self, riggings, skeletons, matrixs):
        self.riggings = riggings
        self.skeletons = skeletons
        self.matrixs = matrixs
        assert(all([isinstance(x, Rigging) for x in riggings]))
        assert(all([isinstance(x, Skeleton) for x in skeletons]))
        for rigging in self.riggings:
            if rigging.skeleton is not None:
                skeleton = self.skeletons[rigging.skeleton]
                assert(all([i >= 0 and i < len(skeleton.names) 
                            for i in rigging.skin.indices]))
            else: assert(len(rigging.skin.indices) == 0)

    @staticmethod
    def load(dir, name):
        path = os.path.join(dir, name + '.npz')
        state = np.load(path, allow_pickle = True)['data'].item()
        return Scene.load_state_dict(state)

    def save(self, dir, name):
        path = os.path.join(dir, name + '.npz')
        np.savez_compressed(path, data = self.state_dict())

    def state_dict(self):
        state = {}
        for i, rigging in enumerate(self.riggings):
            state['mesh_' + str(i)] = rigging.state_dict()
        for i, skeleton in enumerate(self.skeletons):
            state['skeleton_' + str(i)] = skeleton.state_dict()
        state['matrix'] = self.matrixs
        return state

    @staticmethod
    def load_state_dict(state):
        number = len([i for i in state.keys() if 'mesh' in i])
        matrixs = state['matrix']
        riggings = [Rigging.load_state_dict(state['mesh_' + str(x)]) 
                    for x in range(number)]
        number = len([i for i in state.keys() if 'skeleton' in i])
        skeletons = [Skeleton.load_state_dict(state['skeleton_' + str(x)])
                     for x in range(number)]
        return Scene(riggings, skeletons, matrixs)

    @staticmethod
    def scene_skeleton(skeletons):
        prefix = [0 if x is None else len(x.names) for x in skeletons]
        prefix = list(accumulate([0] + prefix))[:-1]
        skeletons = [x for x in skeletons if x is not None]
        if len(skeletons) == 0: return None
        positions = np.concatenate([x.positions for x in skeletons])
        names = sum([x.names for x in skeletons], [])
        parents = np.concatenate([[-1 if y == -1 else y + prefix[i] 
                for y in x.parents] for i, x in enumerate(skeletons)])
        matrixs = np.concatenate([x.matrixs for x in skeletons])
        skeleton = Skeleton(names, positions, parents, matrixs)
        return skeleton, prefix

    @staticmethod
    def scene_mesh(meshes):
        vertex_num = [len(x.vertices) for x in meshes]
        prefix = list(accumulate([0] + vertex_num))
        vertices = np.concatenate([x.vertices for x in meshes])
        normals = np.concatenate([x.normals for x in meshes])
        triangles = np.concatenate([x.triangles + prefix[i] 
                                    for i, x in enumerate(meshes)])
        return Mesh(vertices, normals, triangles)

    @staticmethod
    def scene_skin(skins, prefix):
        numbers = np.concatenate([x.numbers for x in skins])
        weights = np.concatenate([x.weights for x in skins])
        indices = np.concatenate([skins[i].indices + prefix[i] 
                                  for i in range(len(prefix))])
        return Skin(numbers, indices, weights)
        
    def combine(self):
        riggings, skeletons, indexs = [], [], []
        for i, mesh in enumerate(self.riggings):
            if mesh.skeleton is not None:
                if mesh.skeleton not in skeletons:
                    skeletons.append(mesh.skeleton)
                indexs.append(skeletons.index(mesh.skeleton))
                jmatrix = self.skeletons[mesh.skeleton].matrixs
            else: 
                jmatrix = None
                indexs.append(None)
            riggings.append(mesh.skin_mesh(jmatrix, self.matrixs[i]))
        skeletons = [self.skeletons[x] for x in skeletons]
        skeleton, prefix = Scene.scene_skeleton(skeletons)
        mesh = Scene.scene_mesh([x.mesh for x in riggings])
        prefix = [prefix[x] if x is not None else None for x in indexs]
        skin = Scene.scene_skin([x.skin for x in riggings], prefix)
        return Rigging(mesh, skeleton, skin)