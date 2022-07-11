import numpy as np
from collada import *

class Geometry:
    @staticmethod
    def parse_geometry(geometric):
        geometry_vertex, geometry_face_normal = [], []
        geometry_triangle = []
        source_ids, vertex_num = {}, 0
        for primitive in geometric.primitives:
            assert('VERTEX' in primitive.sources)
            source = primitive.sources['VERTEX']
            assert(len(source) == 1)
            source_id, source_num = source[0][2], len(source[0][4])
            parse_result = Geometry.parse_primitive(primitive)
            if parse_result is None: continue
            vertices, normals, triangles = parse_result
            if source_id not in source_ids:
                source_ids[source_id] = vertex_num
                vertex_num += len(vertices)
                assert(len(vertices) == source_num)  
                geometry_vertex.append(vertices)
            geometry_face_normal.append(normals)
            geometry_triangle.append(triangles + source_ids[source_id])
        vertices = np.concatenate(geometry_vertex)
        face_normals = np.concatenate(geometry_face_normal)
        triangles = np.concatenate(geometry_triangle)
        normals = Geometry.calculate_vertex_normal(vertices, triangles, face_normals)
        return vertices, normals, triangles

    @staticmethod
    def parse_primitive(primitive):
        face_index = Geometry.get_face_index(primitive)
        if face_index is None: return None
        vertices = primitive.vertex
        triangles = np.array(primitive.vertex_index).reshape(-1)
        triangles = triangles[face_index].reshape(-1)
        if primitive.normal is not None:
            normals = np.array(primitive.normal)
            normal_index = np.array(primitive.normal_index).reshape(-1)
            normal_index = normal_index[face_index].reshape(-1)
            face_normals = normals[normal_index]
        else: face_normals = Geometry.calculate_face_normal(vertices, triangles)
        return vertices, face_normals, triangles
        
    @staticmethod
    def get_face_index(primitive):
        if isinstance(primitive, geometry.polylist.Polylist):
            assert(len(primitive.polystarts) == len(primitive.polyends))
            face_index = []
            for i in range(len(primitive.polystarts)):
                start = primitive.polystarts[i]
                end = primitive.polyends[i]
                for j in range(start + 1, end - 1):
                    face_index.append([start, j, j + 1])
            face_index = np.array(face_index)
        elif isinstance(primitive, geometry.triangleset.TriangleSet):
            face_index = np.arange(primitive.ntriangles * 3).reshape(-1, 3)
        else: 
            assert(isinstance(primitive, geometry.lineset.LineSet))
            face_index = None
        return face_index

    @staticmethod
    def calculate_face_normal(vertices, triangles):
        face_normals = []
        for i in range(0, len(triangles), 3):
            vertex_a = vertices[triangles[i]]
            vertex_b = vertices[triangles[i + 1]]
            vertex_c = vertices[triangles[i + 2]]
            vector_a = vertex_b - vertex_a
            vector_b = vertex_c - vertex_a
            normal = np.cross(vector_a, vector_b)
            if np.linalg.norm(normal) < 1e-8:
                normal = [0, 1.0, 0]
            else: normal = normal / np.linalg.norm(normal)
            face_normals.append([normal, normal, normal])
        return np.array(face_normals).reshape(-1, 3)

    @staticmethod
    def calculate_vertex_normal(vertices, triangles, face_normals):
        areas, normal_set = [], [[] for _ in range(len(vertices))]
        for i in range(len(triangles) // 3):
            a, b, c = map(lambda x: vertices[triangles[i * 3 + x]], [0, 1, 2])
            areas.append(np.linalg.norm(np.cross(a - b, a - c)))
        for i, index in enumerate(triangles):
            normal_set[index].append((face_normals[i], areas[i // 3]))
        normals = np.ones(vertices.shape)
        for i in range(len(normal_set)):
            if len(normal_set[i]) <= 0: continue
            normal = [x * weight for x, weight in normal_set[i]]
            normal = np.sum(normal, 0)
            if np.linalg.norm(normal) < 1e-8:
                normal = normal_set[i][0][0]
            if np.linalg.norm(normal) >= 1e-8:
                normals[i] = normal
        normals = normals / np.linalg.norm(normals, axis = 1)[:, np.newaxis]
        return normals 