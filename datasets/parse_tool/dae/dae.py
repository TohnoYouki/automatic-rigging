import numpy as np
from collada import *
from .scene import Scene
from .reader import Reader
from .controller import Controller

class DAE:
    @staticmethod
    def transform(scene, upaxis):
        if upaxis == 'Y_UP':
            matrix = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        elif upaxis == 'Z_UP':
            matrix = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        else: assert(False)
        scene.vertices = np.matmul(matrix, scene.vertices.T).T
        scene.normals = np.matmul(np.linalg.inv(matrix).T, scene.normals.T).T
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
