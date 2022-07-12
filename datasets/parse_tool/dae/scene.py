import json
import numpy as np
from collada import *
from .skeleton import Skeleton
from .controller import Controller

class Scene:
    def __init__(self, collada_scene):
        assert(isinstance(collada_scene, scene.Scene))
        skeletons = Skeleton(collada_scene)
        controllers = Controller(collada_scene)
        self.check_controllers(skeletons, controllers)
        self.combine(controllers)
        self.joint_name = skeletons.names
        self.joint_position = skeletons.positions
        self.joint_parent = skeletons.parents
        if self.vertices is not None:
            assert(len(self.vertices) == len(self.skins))

    def save(self, name, directory):
        path = directory + name + '.json'
        info = {'vertex': [str(x) for x in self.vertices.reshape(-1)], 
                'normal': [str(x) for x in self.normals.reshape(-1)], 
                'triangle': self.triangles.tolist(), 
                'joint_name': self.joint_name,
                'joint_position': [str(x) for x in self.joint_position.reshape(-1)],
                'joint_parent': self.joint_parent.tolist(), 
                'joint_skin': [[[i, str(w)] for i, w in y] for y in self.skins]}
        with open(path, 'w') as file:
            content = json.dumps(info)
            file.write(content)

    def controllers_joint_set(self, skeletons, controller):
        joints = []
        for ref_id in controller['skeleton']:
            match_items = []
            for node, indexs in skeletons.ref:
                if hasattr(node, 'id') and node.id == ref_id:
                    match_items.append(indexs)
                elif node.xmlnode.get('sid', None) == ref_id:
                    match_items.append(indexs)
                elif node.xmlnode.get('name', None) == ref_id:
                    match_items.append(indexs)
            if len(match_items) == 0: continue
            match_items = [x for x in match_items if len(x) > 0]
            for index in match_items[-1]: 
                joints.append(index)
        if len(controller['skeleton']) == 0:
            joints = [x for x in range(len(skeletons.ids))]
        return sorted(list(set(joints)))

    def check_controllers(self, skeletons, controllers):
        for controller in controllers.controller:
            joints = self.controllers_joint_set(skeletons, controller)
            sids = controller['sid']
            index_map = []
            joint_sids = [skeletons.sids[i] for i in joints]
            if sids != joint_sids:
                for sid in controller['sid']:
                    indexs = []
                    for joint in joints:
                        if skeletons.sids[joint] == sid:
                            indexs.append(joint)
                    assert(len(indexs) <= 1)
                    if len(indexs) == 1:
                        index_map.append(indexs[0])
                    else: index_map.append(None)
                if index_map.count(None) > 0: raise Exception('Joint ref error!')
            else: index_map = [x for x in range(len(sids))]
            controller['index_map'] = index_map   

    def combine(self, controllers):
        vertex_num = 0
        vertices, normals, triangles, skins = [], [], [], []
        for controller in controllers.controller:
            if 'index_map' not in controller: continue
            vertices.append(controller['vertex'])
            normals.append(controller['normal'])
            triangles.append(controller['triangle'] + vertex_num)
            vertex_num += len(vertices)
            skins.extend([[[controller['index_map'][i], w] 
                            for i, w in y] for y in controller['skin']])
        self.skins = skins
        if len(vertices) > 0:
            self.vertices = np.concatenate(vertices)
            self.normals = np.concatenate(normals)
            self.triangles = np.concatenate(triangles)
        else: self.vertices = self.normals = self.triangles = None