import numpy as np
from collada import *

class Skeleton:
    def __init__(self, collada_scene):
        assert(isinstance(collada_scene, scene.Scene))
        scene_nodes = collada_scene.nodes
        self.ids, self.sids, self.names = [], [], []
        self.parents, self.positions, self.ref = [], [], []
        self.ref.append([collada_scene, None])
        self.collate_skeleton(scene_nodes)
        self.ref[0][1] = range(len(self.ids))
        self.parents = np.array(self.parents)
        self.positions = np.array(self.positions)

    def collate_skeleton(self, nodes, parent = -1, parent_matrix = np.identity(4)):
        for node in nodes:
            prev_len = len(self.ids)
            if hasattr(node, 'matrix'):
                local_matrix = node.matrix
            else: local_matrix = np.identity(4)
            global_matrix = np.matmul(parent_matrix, local_matrix)
            if node.xmlnode.get('type', None) == 'JOINT':
                info_dict = dict(node.xmlnode.items())
                self.ids.append(info_dict['id'])
                if 'sid' in info_dict: self.sids.append(info_dict['sid'])
                else: self.sids.append(info_dict['id'])
                self.names.append(info_dict['name'])
                self.positions.append(global_matrix[:3, 3] / global_matrix[3:, 3])
                self.parents.append(parent)
                node_index = len(self.ids) - 1
            else: node_index = parent
            if hasattr(node, 'children'):
                self.collate_skeleton(node.children, node_index, global_matrix)
            self.ref.append([node, range(prev_len, len(self.ids))])