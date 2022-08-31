import numpy as np
from scipy.spatial.transform import Rotation as R

def split_array(content, fn):
    cursor, result = 0, []
    while cursor < len(content):
        if len(content[cursor]) == 0:
            cursor += 1
            continue
        assert(fn(content[cursor]))
        for end in range(cursor + 1, len(content) + 1):
            if end >= len(content): break
            if len(content[end]) == 0 or fn(content[end]): break
        result.append(content[cursor:end])
        cursor = end
    return result

class SkeletalAnimation:
    def __init__(self, ids, names, parents, skeletons):
        self.ids = ids
        self.names = names
        self.parents = parents
        self.skeletons = skeletons

    def joint_pos(self, frame, parents):
        cursor, number = 0, 0
        local = {x:[y, z] for x, y, z in self.skeletons[frame]}
        local = [local[id] for id in self.ids]
        world = [[None, None] for _ in range(len(local))]
        while any([x[0] is None for x in world]):
            local_pos, local_euler = local[cursor]
            local_pos = np.array(local_pos)
            local_matrix = R.from_euler('xyz', local_euler, False)
            if parents[cursor] == -1:
                world[cursor] = [local_pos, local_matrix]
            elif world[parents[cursor]][0] is not None:
                parent_pos, parent_matrix = world[parents[cursor]]
                world_pos = parent_matrix.apply(local_pos)
                world_pos += parent_pos
                world_matrix = parent_matrix * local_matrix
                world[cursor] = [world_pos, world_matrix]
            cursor = (cursor + 1) % len(world)
            number += 1
            if number > len(local) * len(local): raise Exception('dead loop')
        result = np.array([x[0] for x in world])
        return result

    @staticmethod
    def parse_nodes(content):
        ids, names, parents = [], [], []
        for node in content:
            name = ''.join([node[i] + ' ' for i in range(1, len(node) - 1)])
            id, parent, name = node[0], node[-1], name[:-1]
            if parent == id: parent = '-1'
            assert(name[0] == '"' and name[-1] == '"')
            if int(id) not in ids:
                ids.append(int(id))
                names.append(name[1:-1])
                parents.append(int(parent))
            else:
                index = ids.index(int(id))
                assert(names[index] == name[1:-1])
                assert(parents[index] == int(parent))
        return ids, names, parents

    @staticmethod
    def parse_skeleton(content):
        frames = split_array(content, lambda x:x[0] == 'time')
        times = [int(x[0][1]) for x in frames]
        assert(all([times[i + 1] > times[i] for i in range(len(times) - 1)]))
        result = []
        for frame in frames:
            result.append({})
            for node in frame[1:]:
                try:
                    id = int(node[0])
                    pos = [float(node) for node in node[1:4]]
                    rot = [float(node) for node in node[4:7]]
                except Exception as e:
                    continue
                else:
                    if id not in result: 
                        result[-1][id] = [pos, rot]
                    else:
                        assert(result[-1][id][0] == pos)
                        assert(result[-1][id][1] == rot)
            result[-1] = [[x, *result[-1][x]] for x in result[-1]]
        result = {times[i]:result[i] for i in range(len(frames))}
        return result

    def remove_uncompiled_node(self):
        frames = sorted([x for x in self.skeletons])
        if len(frames) > 0:
            start_frame = frames[0]
            skeleton_ids = set([x[0] for x in self.skeletons[start_frame]])
            compiled = [i for i in range(len(self.ids)) 
                        if self.ids[i] in skeleton_ids]
            self.ids = [self.ids[x] for x in compiled]
            self.names = [self.names[x] for x in compiled]
            self.parents = [self.parents[x] for x in compiled]
            assert(len(skeleton_ids) == len(self.ids))

    @staticmethod
    def check_correct(ids, parents, skeletons):
        assert(all([x == -1 or x in ids for x in parents]))
        assert(len(set(ids)) == len(ids))
        assert(all([all([y[0] in ids for y in skeletons[x]]) for x in skeletons]))   

    @staticmethod
    def generate(node_content, skeleton_content):
        if node_content is None or skeleton_content is None: return None
        ids, names, parents = SkeletalAnimation.parse_nodes(node_content)
        skeletons = SkeletalAnimation.parse_skeleton(skeleton_content)
        SkeletalAnimation.check_correct(ids, parents, skeletons)
        if len(ids) > 0:
            return SkeletalAnimation(ids, names, parents, skeletons)
        else: return None