import numpy as np

class StaticMesh:
    def __init__(self, triangles):
        self.material = [x[0] for x in triangles]
        self.parent = np.array([x[1] for x in triangles])
        self.vertices = np.array([x[2] for x in triangles])
        self.normals = np.array([x[3] for x in triangles])
        self.uvs = np.array([[x[4] for x in triangles]])
        self.skins = [x[5] for x in triangles]
        self.triangles = np.array([x for x in range(len(triangles))])
        self.triangles = self.triangles.reshape(-1, 3)
    
    @staticmethod
    def parse_vertex_attribute(triangle):
        vertices = np.array([[float(y) for y in x[1:4]] for x in triangle])
        uvs = [[float(y) for y in x[7:9]] for x in triangle]
        edge = (vertices[0] - vertices[1], vertices[0] - vertices[2])
        calculate_normal = np.cross(edge[0], edge[1])
        normals = []
        for i in range(3):
            try: normal = [float(y) for y in triangle[i][4:7]]
            except:
                norm = np.linalg.norm(calculate_normal)
                if norm < 1e-3: normals.append([1.0, 0.0, 0.0])
                else: normals.append(calculate_normal / norm)
            else: normals.append(normal)
        return vertices, normals, uvs

    @staticmethod
    def parse_skin(triangle):
        parents, skins = [int(x[0]) for x in triangle], []
        for i in range(3):
            vertex = triangle[i]
            skin_num = int(vertex[9]) if len(vertex) > 9 else 0
            skin = [[] for _ in range(skin_num)]
            for j in range(len(skin)):
                skin[j] = [int(vertex[10 + 2 * j]), float(vertex[11 + 2 * j])]
            if 1.0 - sum([x[1] for x in skin], 0.0) > 3e-3:
                skin.append([parents[i], 1.0 - sum([x[1] for x in skin])])
            skins.append(skin)
        return parents, skins

    @staticmethod
    def parse_triangles(content):
        assert(len(content) % 4 == 0)
        triangles = [content[i:i + 4] for i in range(0, len(content), 4)]
        result = []
        for triangle in triangles:
            material = triangle[0][0] if len(triangle[0]) > 0 else None
            try:
                fn = StaticMesh.parse_vertex_attribute
                vertices, normals, uvs = fn(triangle[1:])
            except: continue
            parents, skins = StaticMesh.parse_skin(triangle[1:])
            for i in range(3):
                result.append([material, parents[i], vertices[i], 
                               normals[i], uvs[i], skins[i]])
        return result

    @staticmethod
    def generate(content):
        if content is None: return None
        triangles = StaticMesh.parse_triangles(content)
        skins = [x[5] for x in triangles]
        assert(all([abs(sum([x[1] for x in y]) - 1.0) < 2e-3 for y in skins]))
        return StaticMesh(triangles)