class Mesh:
    def __init__(self, vertices, normals, triangles):
        self.vertices = vertices
        self.normals = normals
        self.triangles = triangles
        assert(len(vertices) == len(normals))
        assert(min([x for x in triangles]) >= 0)
        assert(max([x for x in triangles]) < len(vertices))