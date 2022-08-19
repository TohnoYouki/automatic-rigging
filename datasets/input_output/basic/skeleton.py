class Skeleton:
    def __init__(self, names, positions, parents):
        self.names = names
        self.positions = positions
        self.parents = parents
        assert(max(parents) < len(self.names))
        assert(min(parents) >= -1)