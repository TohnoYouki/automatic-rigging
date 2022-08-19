import numpy as np

class Skeleton:
    def __init__(self, name, joints, matrixs, parents, ib_matrixs):
        self.name = name
        self.joints = joints
        self.global_matrixs = matrixs
        self.positions = np.array([x[:3, 3] / x[3, 3] for x in matrixs])
        self.parents = parents
        self.inverse_bind_matrixs = ib_matrixs
        self.joint_matrixs = np.array([np.matmul(matrixs[i], ib_matrixs[i])
                                       for i in range(len(parents))])

    @staticmethod
    def build_hierarchy(node, parent, joints, parents):
        if node in joints:
            index = joints.index(node)
            parents[index] = parent
        for child in node.children:
            if node in joints:
                Skeleton.build_hierarchy(child, node, joints, parents)
            else: Skeleton.build_hierarchy(child, parent, joints, parents)

    @staticmethod
    def parse(skin, nodes, accessors):
        root = nodes[skin.skeleton]
        joints = [nodes[x] for x in skin.joints]
        parents = [None for _ in skin.joints]
        Skeleton.build_hierarchy(root, None, joints, parents)
        parents = [joints.index(x) if x in joints else -1 for x in parents]
        assert(parents.count(-1) == 1)
        assert(parents.index(-1) == joints.index(root))
        matrixs = [x.global_matrix for x in joints]
        names = [x.name for x in joints]
        ib_matrix = accessors[skin.inverseBindMatrices]
        ib_matrix = ib_matrix.transpose(0, 2, 1)
        return Skeleton(skin.name, names, matrixs, parents, ib_matrix)

def parse_skeleton(gltf, nodes, accessors):
    skeletons = [Skeleton.parse(x, nodes, accessors) for x in gltf.skins]
    indices = sum([x.joints for x in gltf.skins], [])
    assert(len(indices) == len(set(indices)))
    for node in nodes:
        if node.skeleton is not None and isinstance(node.skeleton, int):
            node.skeleton = skeletons[node.skeleton]
    return skeletons