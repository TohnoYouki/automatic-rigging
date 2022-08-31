import numpy as np
from collada import *
from itertools import accumulate

class JointSets:
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
                position = global_matrix[:3, 3] / global_matrix[3:, 3]
                self.positions.append(position)
                self.parents.append(parent)
                node_index = len(self.ids) - 1
            else: node_index = parent
            if hasattr(node, 'children'):
                params = (node.children, node_index, global_matrix)
                self.collate_skeleton(*params)
            self.ref.append([node, range(prev_len, len(self.ids))])

class PartialSkeleton:
    def __init__(self, ids, sids, names, positions, parents):
        self.ids = ids
        self.sids = sids
        self.names = names
        self.positions = positions
        self.parents = parents

    @staticmethod
    def extract_partial_indices(joint_sets):
        number = len(joint_sets.parents)
        skeletons, pending = [], [i for i in range(number)]
        while len(pending) > 0:
            parents = joint_sets.parents
            pop_index = [x for x in pending if parents[x] not in pending]
            for i in pop_index:
                skeleton = [x for x in skeletons if parents[i] in x]
                assert(len(skeleton) <= 1)
                if len(skeleton) == 0:
                    skeletons.append([i])
                else: skeleton[0].append(i)
                pending.remove(i)
        skeletons = [sorted(x) for x in skeletons]
        indices = sorted(sum([x for x in skeletons], []))
        assert(number == len(indices))
        assert(all([i == indices[i] for i in range(len(indices))]))
        skeletons = sorted(skeletons, key = lambda x:x[0])
        return skeletons

    @staticmethod
    def create_partial_skeleton(joint_sets):
        assert(isinstance(joint_sets, JointSets))
        result, refs = [], [[x[0], []] for x in joint_sets.ref]
        skeletons = PartialSkeleton.extract_partial_indices(joint_sets)
        for i, indices in enumerate(skeletons):
            for j in range(len(joint_sets.ref)):
                if any([x in joint_sets.ref[j][1] for x in indices]):
                    refs[j][1].append(i)
            ids, sids, names, positions, parents = \
                map(lambda x:[getattr(joint_sets, x)[y] for y in indices],
                    ('ids', 'sids', 'names', 'positions', 'parents'))
            parents = [x if x == -1 else indices.index(x) for x in parents]
            params = (ids, sids, names, positions, parents)
            result.append(PartialSkeleton(*params))
        return result, refs

class Skeleton:
    def __init__(self, ids, sids, names, positions, parents):
        self.ids = ids
        self.sids = sids
        self.names = names
        self.positions = positions
        self.parents = parents

    @staticmethod
    def generate(collada_scene, controllers):
        joints = JointSets(collada_scene)
        partials, refs = PartialSkeleton.create_partial_skeleton(joints)
        nodes = [x[0] for x in refs]
        node_index = [nodes.index(x['node']) for x in controllers]
        node_range = [node_index[i] for i in range(len(node_index))]
        refs = [Skeleton.find_partial_skeleton(refs, x, partials, y) 
                for x, y in zip(controllers, node_range)]
        skeletons, refs = Skeleton.combine_refs(refs)
        skeletons = [[partials[y] for y in x] for x in skeletons]
        skeletons = [Skeleton.combine_partial_skeleton(x) for x in skeletons]
        return skeletons, refs

    @staticmethod
    def find_partial_skeleton(refs, controller, partials, index_upper):
        result = []
        skeletons = controller['skeleton']
        if len(skeletons) == 0:
            for sid in controller['sid']:
                match_items = [i for i in range(len(partials))
                               if sid in partials[i].sids]
                assert(len(match_items) == 1)
                result.append(match_items[0])
            result = sorted(list(set(result)))
        else:
            for ref_id in skeletons:
                match_items = []
                for i, (node, _) in enumerate(refs):
                    if hasattr(node, 'id') and node.id == ref_id:
                        match_items.append(i)
                    elif node.xmlnode.get('sid', None) == ref_id:
                        match_items.append(i)
                    elif node.xmlnode.get('name', None) == ref_id:
                        match_items.append(i)
                if len(match_items) == 0: continue
                if len(match_items) > 1:
                    match_items = [x for x in match_items if x < index_upper]
                result.extend(refs[match_items[-1]][1])
            result = sorted(list(set(result)))
        assert(len(result) > 0)
        return result            

    @staticmethod
    def combine_refs(refs):
        skeletons, skeleton_ids = [], []
        for indices in refs:
            skeleton_id = -1
            for i, skeleton in enumerate(skeletons):
                if any([x in skeleton for x in indices]):
                    skeleton_id = i
            if skeleton_id == -1:
                skeleton_ids.append(len(skeletons)) 
                skeletons.append(indices)
            else:
                skeleton_ids.append(skeleton_id)
                skeletons[skeleton_id].extend(indices)
        skeletons = [sorted(set(x)) for x in skeletons]
        return skeletons, skeleton_ids

    @staticmethod
    def combine_partial_skeleton(partials):
        attrs = ['ids', 'sids', 'names', 'positions', 'parents']
        attrs = list(map(lambda x:[getattr(y, x) for y in partials], attrs))
        prefix = [0] + list(accumulate([len(x) for x in attrs[-1]]))
        for i in range(len(prefix) - 1):
            attrs[-1][i] = [x + prefix[i] if x >= 0 else -1 
                            for x in attrs[-1][i]]
        attrs = map(lambda x:sum(x, []), attrs)
        ids, sids, names, positions, parents = attrs
        return Skeleton(ids, sids, names, positions, parents)