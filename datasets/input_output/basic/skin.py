import numpy as np

class Skin:
    def __init__(self, numbers, indices, weights, matrixs = None):
        self.numbers = numbers
        self.indices = indices
        self.weights = weights
        self.inverse_bind_matrixs = matrixs
        assert(min(numbers) >= 0)
        assert(sum(numbers) == len(indices))
        assert(len(self.indices) == len(self.weights))
        if len(indices) > 0:
            assert(min(indices) >= 0)

    def state_dict(self):
        state = {}
        state['number'] = self.numbers
        state['index'] = self.indices
        state['weight'] = self.weights
        state['matrix'] = self.inverse_bind_matrixs
        return state

    @staticmethod
    def load_state_dict(state):
        numbers = state['number']
        indices = state['index']
        weights = state['weight']
        matrixs = state['matrix']
        return Skin(numbers, indices, weights, matrixs)

    @staticmethod
    def from_vertex_skins(skins):
        numbers, indices, weights = [], [], []
        for i in range(len(skins)):
            numbers.append(len(skins[i]))
            for index, weight in skins[i]:
                indices.append(index)
                weights.append(weight)
        numbers, indices, weights = \
            map(lambda x:np.array(x), (numbers, indices, weights))
        return Skin(numbers, indices, weights)

    def vertex_skins(self):
        cursor = 0
        result = [[] for i in range(len(self.numbers))]
        for i in range(len(result)):
            if self.numbers[i] == 0: continue
            indices = self.indices[cursor:cursor + self.numbers[i]]
            weights = self.weights[cursor:cursor + self.numbers[i]]
            cursor += self.numbers[i]
            sum_weight = np.sum(weights)
            if sum_weight < 1e-4: continue
            norm_weights = weights / sum_weight
            result[i] = [[j, w] for j, w in zip(indices, norm_weights)]
        return result