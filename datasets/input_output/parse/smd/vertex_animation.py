from .skeletal_animation import split_array

class VertexAnimation:
    def __init__(self, mesh, vat):
        self.mesh = mesh
        self.vat = vat

    @staticmethod
    def parse(content):
        if content is None: return None
        frames = split_array(content, lambda x:x[0] == 'time')
        times = [int(x[0][1]) for x in frames]
        num = len(frames)
        assert(all([times[i + 1] > times[i] for i in range(num - 1)]))
        result = [[[int(x[0]), [float(x) for x in x[1:4]], 
                   [float(x) for x in x[4:7]]] for x in y[1:]] for y in frames]
        result = {times[i]:result[i] for i in range(num)}
        return result

    @staticmethod
    def generate(mesh, vat):
        vertex_num = mesh.vertices
        frames = sorted([x for x in vat])
        assert(all([all([x[0] >= 0 for x in vat[y]]) for y in vat]))
        assert(all([all([x[0] < vertex_num for x in vat[y]]) for y in vat]))
        if len(frames) > 0:
            assert(len(set([x[0] for x in vat[frames[0]]])) == vertex_num)
        return VertexAnimation(mesh, vat)