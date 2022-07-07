import json
import numpy as np

class RiggingMesh:
    def __init__(self, skeleton, mesh):
        self.skeleton = skeleton
        self.mesh = mesh

    @staticmethod
    def check_correct(skeleton, mesh):
        if not all([x in skeleton.ids for x in mesh.parent]): return False
        if not all([all([x[0] in skeleton.ids for x in y]) 
                    for y in mesh.skins]): return False
        return True

    @staticmethod
    def generate(skeleton, mesh):
        return RiggingMesh(skeleton, mesh)

    def transform(self):
        ids = self.skeleton.ids
        parents = self.skeleton.parents
        parents = [x if x == -1 else ids.index(x) for x in parents]
        parents = np.array(parents)
        skins = [[[ids.index(x), y] for x, y in skin]
                   for skin in self.mesh.skins]
        joint_position = self.skeleton.joint_pos(0)
        return parents, joint_position, skins

    def save(self, name, directory):
        path = directory + name + '.json'
        parents, joint_pos, skins = self.transform()
        info = {'vertex': [str(x) for x in self.mesh.vertices.reshape(-1)], 
                'normal': [str(x) for x in self.mesh.normals.reshape(-1)], 
                'triangle': self.mesh.triangles.reshape(-1).tolist(), 
                'joint_name': self.skeleton.names,
                'joint_position': [str(x) for x in joint_pos.reshape(-1)],
                'joint_parent': parents.tolist(), 
                'joint_skin': skins}
        with open(path, 'w') as file:
            content = json.dumps(info)
            file.write(content)