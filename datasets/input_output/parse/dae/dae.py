import numpy as np
from collada import *
from .fixer import Fixer
from .skeleton import Skeleton
from .controller import Controller

class DAE:
    @staticmethod
    def generate(file):
        result = []
        collada = Collada(Fixer.fix(file))
        assert(collada is not None)
        result = [Scene(scene) for scene in collada.scenes]
        result = [x for x in result if len(x.meshes) > 0]
        for scene in result:
            scene.transform(collada.assetInfo.upaxis)
        return result

class Scene:
    def __init__(self, collada_scene):
        assert(isinstance(collada_scene, scene.Scene))
        nodes = Controller(collada_scene).controllers
        controllers = [x for x in nodes if x['skeleton'] is not None]
        skeletons, refs = Skeleton.generate(collada_scene, controllers)
        for i in range(len(controllers)):
            self.remap_joint_index(controllers[i], skeletons[refs[i]])
            controllers[i]['skeleton'] = refs[i]
        self.skeletons = skeletons
        self.meshes = [x['geometry'] for x in nodes]
        self.matrixs = [x['matrix'] for x in nodes]
        self.refs = [x['skeleton'] for x in nodes]

    def transform(self, upaxis):
        if upaxis == 'Y_UP':
            matrix = np.array([[1, 0, 0, 0], [0, 0, 1, 0], 
                               [0, -1, 0, 0], [0, 0, 0, 1]])
        elif upaxis == 'Z_UP':
            matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], 
                               [0, 0, 1, 0], [0, 0, 0, 1]])
        else: assert(False)
        self.matrixs = [np.matmul(matrix, x) for x in self.matrixs]
        for skeleton in self.skeletons:
            positions = np.array(skeleton.positions)
            skeleton.positions = np.matmul(matrix[:3, :3], positions.T).T

    def remap_joint_index(self, controller, skeleton):
        imap = []
        sids, joint_sids = controller['sid'], skeleton.sids
        if sids != joint_sids:
            for sid in sids:
                indexs = [i for i in range(len(joint_sids)) 
                          if sid == joint_sids[i]]
                assert(len(indexs) == 1)
                imap.append(indexs[0])
        else: imap = [x for x in range(len(sids))]
        skins = controller['geometry'].skins
        for i in range(len(skins)):
            skins[i] = [[imap[j], w] for j, w in skins[i]]