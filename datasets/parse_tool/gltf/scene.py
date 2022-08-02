import json
import numpy as np
from mesh import Geometry
from skeleton import Skeleton
from itertools import accumulate

class Scene:
    def __init__(self, name, vertices, normals, triangles, 
                       joint_names, parents, joint_pos, skins):
        self.name = name
        self.vertices = vertices
        self.normals = normals
        self.triangles = triangles
        self.joint_name = joint_names
        self.joint_parent = parents
        self.joint_position = joint_pos
        self.skins = skins

    def save(self, name, directory):
        path = directory + name + '.json'
        info = {'vertex': [str(x) for x in self.vertices.reshape(-1)],
                'normal': [str(x) for x in self.normals.reshape(-1)],
                'triangle': self.triangles.tolist(),
                'joint_name': self.joint_name,
                'joint_position': [str(x) for x in self.joint_position.reshape(-1)],
                'joint_parent': self.joint_parent.tolist(),
                'joint_skin': [[[int(i), str(w)] for i, w in y] for y in self.skins]}
        with open(path, 'w') as file:
            content = json.dumps(info)
            file.write(content)

    @staticmethod
    def node_set(node):
        result = []
        for child in node.children:
            nodes = [x for x in Scene.node_set(child) if x not in result]
            result.extend(nodes)
        result.append(node)
        return result

    @staticmethod
    def scene_nodes(scene, nodes):
        root_nodes = [nodes[x] for x in scene.nodes]
        node_sets = [Scene.node_set(x) for x in root_nodes]
        scene_nodes = []
        for node_set in node_sets:
            for node in node_set: 
                if node not in scene_nodes: 
                    scene_nodes.append(node)
        return scene_nodes

    @staticmethod
    def scene_skeleton(nodes):
        skeletons, names = [], []
        for i in range(len(nodes)):
            if nodes[i].skeleton is None: continue
            if not isinstance(nodes[i].skeleton, Skeleton): continue
            if nodes[i].skeleton in skeletons: continue
            skeletons.append(nodes[i].skeleton)
        if len(skeletons) <= 0: return None
        positions = np.concatenate([x.positions for x in skeletons])
        for x in skeletons: names.extend(x.joints)
        num = [len(x.positions) for x in skeletons]
        prefix = list(accumulate([0] + num))
        parents = np.concatenate([[-1 if y == -1 else y + prefix[i] 
                for y in x.parents] for i, x in enumerate(skeletons)])
        return positions, parents, names, skeletons, prefix

    @staticmethod
    def parse(scene, nodes):
        scene_nodes = Scene.scene_nodes(scene, nodes)
        scene_skeleton = Scene.scene_skeleton(scene_nodes)
        if scene_skeleton is not None:
            joint_pos, parents, names, skeletons, prefixs = scene_skeleton
        meshes = [x.global_mesh() for x in scene_nodes]
        for i, mesh in enumerate(meshes):
            if mesh is None: continue
            if scene_nodes[i].skeleton is None: continue
            assert(scene_nodes[i].skeleton in skeletons)
            prefix = prefixs[skeletons.index(scene_nodes[i].skeleton)]
            for j in range(len(mesh.skins)):
                for k in range(len(mesh.skins[j])):
                    mesh.skins[j][k][0] += prefix
        meshes = [x for x in meshes if x is not None]
        mesh = Geometry.merge_geometries(meshes)
        if scene_skeleton is None: return mesh
        vertices, normals = mesh.vertices, mesh.normals
        triangles, skins = mesh.triangles, mesh.skins
        return Scene(scene.name, vertices, normals, triangles,
                     names, parents, joint_pos, skins)