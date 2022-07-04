import numpy as np
from collada import *
from .scene import Scene
from .reader import Reader

class DAE:
    @staticmethod
    def transform(scene, upaxis):
        min_v = np.min(scene.vertices, 0)
        max_v = np.max(scene.vertices, 0)
        middle = (min_v + max_v) / 2
        scale = np.max(max_v - min_v)
        scene.vertices = (scene.vertices - middle) / scale
        scene.joint_position = (scene.joint_position - middle) / scale
        if upaxis == 'Y_UP':
            matrix = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        elif upaxis == 'Z_UP':
            matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        else: assert(False)
        scene.vertices = np.matmul(matrix, scene.vertices.T).T
        scene.joint_position = np.matmul(matrix, scene.joint_position.T).T

    @staticmethod
    def generate(path):
        result = []
        collada = Reader.load(path)
        if collada is None: return None
        result = [Scene(scene) for scene in collada.scenes]
        result = [x for x in result if x.vertices is not None]
        for scene in result:
            DAE.transform(scene, collada.assetInfo.upaxis)
        return result