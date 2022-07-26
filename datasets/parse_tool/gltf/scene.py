import json
import numpy as np
from mesh import Geometry
from itertools import accumulate

class Scene:
    def __init__(self, vertices, normals, triangles, 
                       names, parents, joint_pos, skins):
        self.vertices = vertices
        self.normals = normals
        self.triangles = triangles
        self.joint_name = names
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
                'joint_skin': [[[i, str(w)] for i, w in y] for y in self.skins]}
        with open(path, 'w') as file:
            content = json.dumps(info)
            file.write(content)

    @staticmethod
    def scene_nodes(scene, nodes):
        root_nodes = [nodes[x] for x in scene.nodes]
        node_sets = [x.node_set() for x in root_nodes]
        scene_nodes = []
        for node_set in node_sets:
            for node in node_set: 
                if node not in scene_nodes: 
                    scene_nodes.append(node)
        return scene_nodes

    @staticmethod
    def scene_skeleton(nodes, skeletons):
        names = []
        indices = set([x.skeleton_index for x in nodes])
        indices.remove(None)
        indices = list(indices)
        positions = [skeletons[x].positions for x in indices]
        positions = np.concatenate(positions)
        for i in indices: names.extend(skeletons[i].joints)
        parents = [skeletons[x].parents for x in indices]
        num = [len(skeletons[x].positions) for x in indices]
        prefix = list(accumulate([0] + num))
        parents = [[-1 if j == -1 else j + prefix[i] 
                    for j in parents[i]] 
                    for i in range(len(parents))]
        parents = np.concatenate(parents)
        index_map = {i: [prefix[i] + j
                     for j in range(len(skeletons[i].positions))]
                     for i in indices}
        return positions, parents, names, index_map

    @staticmethod
    def parse(scene, skeletons, nodes):
        scene_nodes = Scene.scene_nodes(scene, nodes)
        scene_skeleton = Scene.scene_skeleton(scene_nodes, skeletons)
        joint_pos, parents, joint_names, index_map = scene_skeleton
        meshes = [x.global_mesh() for x in scene_nodes]
        for i, mesh in enumerate(meshes):
            if mesh is None: continue
            for j in range(len(mesh.skins)):
                for k in range(len(mesh.skins[j])):
                    index = mesh.skins[j][k][0]
                    sindex = scene_nodes[i].skeleton_index
                    mesh.skins[j][k][0] = index_map[sindex][index]
        meshes = [x for x in meshes if x is not None]
        mesh = Geometry.merge_geometries(meshes)
        vertices, normals = mesh.vertices, mesh.normals
        triangles, skins = mesh.triangles, mesh.skins
        return Scene(vertices, normals, triangles,
                     joint_names, parents, joint_pos, skins)