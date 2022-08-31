class Skeleton:
    def __init__(self, names, positions, parents, matrixs):
        self.names = names
        self.positions = positions
        self.parents = parents
        self.matrixs = matrixs
        if len(names) > 0:
            assert(max(parents) < len(self.names))
            assert(min(parents) >= -1)
            assert(len(names) == len(positions))
            assert(len(names) == len(parents))
            assert(len(names) == len(matrixs))

    def state_dict(self):
        state = {}
        state['name'] = self.names
        state['position'] = self.positions
        state['parent'] = self.parents
        state['matrix'] = self.matrixs
        return state

    @staticmethod
    def load_state_dict(state):
        names = state['name']
        positions = state['position']
        parents = state['parent']
        matrixs = state['matrix']
        return Skeleton(names, positions, parents, matrixs)