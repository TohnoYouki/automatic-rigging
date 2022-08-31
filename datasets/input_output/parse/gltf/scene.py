import numpy as np

class Scene:
    def __init__(self, name, riggings, partials):
        self.name = name
        self.names, self.matrixs = [], []
        self.meshes, self.skeleton_ref = [], []
        self.inverse_bind_matrixs = []
        for rigging in riggings:
            name, mesh, skeleton, matrix = rigging
            self.matrixs.append(matrix)
            self.meshes.append(mesh)
            self.names.append(name)
            if skeleton is not None:
                self.skeleton_ref.append(partials[skeleton])
            else: self.skeleton_ref.append(None)
        self.remap_skeleton(partials)

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
    def parse(scene, nodes, skeletons):
        result = []
        scene_nodes = Scene.scene_nodes(scene, nodes)
        result = [[x.name, *x.rigging_mesh(), x.global_matrix] 
                   for x in scene_nodes]
        result = [x for x in result if x[1] is not None]
        return Scene(scene.name, result, skeletons)

    def remap_skeleton(self, partials):
        skeletons = list(set([x.skeleton for x in partials]))
        for i in range(len(self.skeleton_ref)):
            partial = self.skeleton_ref[i]
            if partial is None: 
                self.inverse_bind_matrixs.append(None)
                continue
            skeleton = partial.skeleton
            ib_matrixs = [np.identity(4) for _ in range(len(skeleton.joints))]
            joint_map = {j:skeleton.joints.index(x) 
                         for j, x in enumerate(partial.joints)}
            for j in range(len(self.meshes[i].skins)):
                skin = self.meshes[i].skins[j]
                for k in range(len(skin)):
                    skin[k][0] = joint_map[skin[k][0]]
            for j in range(len(partial.joints)):
                ib_matrixs[joint_map[j]] = partial.inverse_bind_matrixs[j]
            self.skeleton_ref[i] = skeletons.index(skeleton)
            self.inverse_bind_matrixs.append(np.array(ib_matrixs))
        self.skeletons = skeletons