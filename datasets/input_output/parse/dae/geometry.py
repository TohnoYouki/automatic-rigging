import numpy as np
from collada import *
from .primitive import Primitive

class Geometry:
    def __init__(self, vertices, normals, triangles, skins):
        self.vertices = vertices
        self.normals = normals
        self.triangles = triangles
        assert(len(vertices) == len(skins))
        self.skins = skins

    @staticmethod
    def parse_skin(control):
        assert(isinstance(control, controller.Skin))
        skins, sids = [], list(control.weight_joints)
        for i in range(len(control.joint_index)):
            skins.append([])
            for j in range(len(control.joint_index[i])):
                joint_index = control.joint_index[i][j]
                if joint_index >= 0:
                    weight = control.weights[control.weight_index[i][j]][0]
                    skins[-1].append([joint_index, weight])
        return sids, skins
    
    @staticmethod
    def parse_node(node):
        mesh = Geometry.parse_geometry(node.geometry)
        if mesh is None: return None
        vertices, normals, triangles = mesh
        if isinstance(node, controller.Skin):
            sids, skins = Geometry.parse_skin(node)
        else: sids, skins = [], [[] for _ in range(len(vertices))]
        return Geometry(vertices, normals, triangles, skins), sids

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
            parse_result = Primitive.parse_primitive(primitive)
            if parse_result is None: continue
            vertices, normals, triangles = parse_result
            if source_id not in source_ids:
                source_ids[source_id] = vertex_num
                vertex_num += len(vertices)
                assert(len(vertices) == source_num)  
                geometry_vertex.append(vertices)
            geometry_face_normal.append(normals)
            geometry_triangle.append(triangles + source_ids[source_id])
        if len(geometry_vertex) == 0: return None
        vertices, face_normals, triangles = map(lambda x:np.concatenate(x),
                (geometry_vertex, geometry_face_normal, geometry_triangle))
        normals = Primitive.calculate_vertex_normal(vertices, triangles, face_normals)
        return vertices, normals, triangles