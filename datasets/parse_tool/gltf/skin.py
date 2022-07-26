class Skeleton:
    def __init__(self, skeleton_name, joint_names, positions, parents):
        self.name = skeleton_name
        self.joints = joint_names
        self.positions = positions
        self.parents = parents

    @staticmethod
    def build_hierarchy(node, parent, joints, parents):
        if node in joints:
            index = joints.index(node)
            parents[index] = parent
        for child in node.children:
            if child in joints:
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
        positions = [x.global_position() for x in joints]
        names = [x.name for x in joints]
        matrix = accessors[skin.inverseBindMatrices]
        '''not implement'''
        return Skeleton(skin.name, names, positions, parents)

def parse_skin(gltf, nodes, accessors):
    skeletons = [Skeleton.parse(x, nodes, accessors) for x in gltf.skins]
    indices = sum([x.joints for x in gltf.skins], [])
    assert(len(indices) == len(set(indices)))
    return skeletons