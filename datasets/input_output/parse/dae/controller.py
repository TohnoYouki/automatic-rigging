import numpy as np
from collada import *
from lxml.etree import _Element
from .geometry import Geometry

class Controller:
    def __init__(self, collada_scene):
        assert(isinstance(collada_scene, scene.Scene))
        self.controllers = []
        scene_nodes = collada_scene.nodes
        self.collate_controller_node(scene_nodes)

    def collate_controller_node(self, nodes, parent_matrix = np.identity(4)):
        for node in nodes:
            if hasattr(node, 'matrix'):
                local_matrix = node.matrix
            else: local_matrix = np.identity(4)
            global_matrix = np.matmul(parent_matrix, local_matrix)
            result = self.parse_node(node, global_matrix)
            if result is not None: 
                self.controllers.append(result)
            if hasattr(node, 'children'):
                self.collate_controller_node(node.children, global_matrix)

    def parse_node(self, node, matrix):
        if isinstance(node, scene.ControllerNode):
            skeleton = []
            for xmlnode in node.xmlnode.getchildren():
                assert(isinstance(xmlnode, _Element))
                if 'skeleton' in xmlnode.tag:
                    skeleton.append(xmlnode.text[1:])
            control = node.controller
            assert(isinstance(control, controller.Skin))
            parse_result = Geometry.parse_node(control)
            if parse_result is None: return None
            geometry, sids = parse_result
            if len(sids) == 0:
                assert(all([len(x) == 0 for x in geometry.skins]))
                skeleton = None
            return {'sid': sids, 'skeleton': skeleton, 
                    'node': node, 'geometry': geometry, 'matrix': matrix}
        elif isinstance(node, scene.GeometryNode):
            parse_result = Geometry.parse_node(node)
            if parse_result is None: return None
            geometry, sids = parse_result
            return {'sid': sids, 'skeleton': None, 
                    'node': node, 'geometry': geometry, 'matrix': matrix}