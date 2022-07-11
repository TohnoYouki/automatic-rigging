import numpy as np
from collada import *
from lxml.etree import _Element
from .primitive import Geometry

class Controller:
    def __init__(self, collada_scene):
        assert(isinstance(collada_scene, scene.Scene))
        self.controller = []
        scene_nodes = collada_scene.nodes
        self.collate_controller_node(scene_nodes)

    @staticmethod
    def parse_skin(control):
        assert(isinstance(control, controller.Skin))
        skins, sids = [], list(control.weight_joints)
        for i in range(len(control.joint_index)):
            skins.append([])
            for j in range(len(control.joint_index[i])):
                joint_index = control.joint_index[i][j]
                weight = control.weights[control.weight_index[i][j]][0]
                if joint_index >= 0:
                    skins[-1].append([joint_index, weight])
        return sids, skins

    @staticmethod
    def transfer(matrix, vertices, normals):
        vertices = np.concatenate((vertices, np.ones((len(vertices), 1))), 1)
        normals = np.concatenate((normals, np.zeros((len(normals), 1))), 1)
        vertices = np.matmul(matrix, vertices.T).T
        normals = np.matmul(np.linalg.inv(matrix).T, normals.T).T
        vertices = vertices[:, :3] / vertices[:, 3:]
        normals = normals[:, :3] / np.linalg.norm(normals, axis = 1)[:, np.newaxis]
        return vertices, normals

    def collate_controller_node(self, nodes, parent_matrix = np.identity(4)):
        for node in nodes:
            if hasattr(node, 'matrix'):
                local_matrix = node.matrix
            else: local_matrix = np.identity(4)
            global_matrix = np.matmul(parent_matrix, local_matrix)
            if isinstance(node, scene.ControllerNode):
                skeleton = []
                for xmlnode in node.xmlnode.getchildren():
                    assert(isinstance(xmlnode, _Element))
                    if 'skeleton' in xmlnode.tag:
                        skeleton.append(xmlnode.text[1:])
                if len(skeleton) <= 0: continue
                control = node.controller
                assert(isinstance(control, controller.Skin))
                sids, skins = Controller.parse_skin(control)
                geometries = Geometry.parse_geometry(control.geometry)
                vertices, normals, triangles = geometries
                assert(len(vertices) == len(skins))
                vertices, normals = Controller.transfer(global_matrix, vertices, normals)
                self.controller.append({'sid': sids, 'skeleton': skeleton, 'skin': skins, 
                'node': node, 'vertex': vertices, 'normal': normals, 'triangle': triangles})
            if hasattr(node, 'children'):
                self.collate_controller_node(node.children, global_matrix)