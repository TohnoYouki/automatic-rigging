import numpy as np

class PartialSkeleton:
    def __init__(self, name, joints, matrixs):
        self.name = name
        self.joints = joints
        self.inverse_bind_matrixs = matrixs
        self.skeleton = None

    @staticmethod
    def parse(skin, nodes, accessors):
        assert(len(skin.joints) == len(set(skin.joints)))
        root = nodes[skin.skeleton]
        joints = [nodes[x] for x in skin.joints]
        assert(root in joints)
        ib_matrix = accessors[skin.inverseBindMatrices]
        ib_matrix = np.array(ib_matrix.transpose(0, 2, 1))
        for i in range(len(ib_matrix)):
            if all(ib_matrix[i][3] == 0.0):
                ib_matrix[i][3][3] = 1.0
        return PartialSkeleton(skin.name, joints, ib_matrix)

class Skeleton:
    def __init__(self, name, joints, parents):
        self.name = name
        self.joints = joints
        self.parents = parents
        self.joint_matrixs = [x.global_matrix for x in joints]
        self.joint_matrixs = np.array(self.joint_matrixs)
        self.names = [x.name for x in joints]
        self.positions = np.array([x[:3, 3] / x[3, 3] 
                         for x in self.joint_matrixs])

    @staticmethod
    def find_parent(node, child, joints):
        if node is not None and node not in joints:
            params = (node.parent, child, joints)
            return Skeleton.find_parent(*params)
        else: return node

    @staticmethod
    def combine_partial_skeletons(skeletons):
        joints = []
        for skeleton in skeletons:
            for i, joint in enumerate(skeleton.joints):
                if joint not in joints:
                    joints.append(joint)
        params = [(x.parent, x, joints) for x in joints]
        parents = [Skeleton.find_parent(*x) for x in params]
        parents = [joints.index(x) if x in joints else -1 for x in parents]
        skeleton = Skeleton(skeletons[0].name, joints, parents)
        for partial in skeletons:
            partial.skeleton = skeleton
        return skeleton

def parse_skeleton(gltf, nodes, accessors):
    skeletons = []
    params = [(x, nodes, accessors) for x in gltf.skins]
    partials = [PartialSkeleton.parse(*x) for x in params]
    for partial in partials:
        overlap = None
        for i in range(len(skeletons)):
            for j in range(len(skeletons[i])):
                joints = skeletons[i][j].joints + partial.joints
                if len(joints) != len(set(joints)): overlap = i
        if overlap is None:
            skeletons.append([partial])
        else: skeletons[overlap].append(partial)
    for x in skeletons:
        Skeleton.combine_partial_skeletons(x)
    for i, skin in enumerate(gltf.skins):
        node = nodes[skin.skeleton]
        if node.skeleton is None:
            node.skeleton = i
        assert(node.skeleton == i)
    return partials