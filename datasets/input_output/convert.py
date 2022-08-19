import os
from .parse import *
from .basic import Rigging

class Converter:
    @staticmethod
    def convert(path):
        if os.path.isfile(path):
            extend = path.split('.')[-1].lower()
            if extend == 'dae':
                result = Converter.convert_dae(path)
            elif extend == 'smd':
                result = Converter.convert_smd(path)
            elif extend == 'gltf' or extend == 'glb':
                result = Converter.convert_gltf(path)
            else: result = None 
        else: result = None
        return result

    @staticmethod
    def convert_dae(path):
        try: 
            colladas = DAE.generate(path)
            if colladas is None: return None
        except Exception as e: 
            return None
        result = []
        for j, collada in enumerate(colladas):
            joint_positions = collada.joint_position.reshape(-1)
            joint_parents = collada.joint_parent
            vertices = collada.vertices.reshape(-1)
            normals = collada.normals.reshape(-1)
            triangles = collada.triangles.reshape(-1)
            mesh = (vertices, normals, triangles)
            skeleton = (collada.joint_name, joint_positions, joint_parents)
            rigging = Rigging.create(*mesh, *skeleton, collada.skins)
            result.append(rigging)
        return result

    @staticmethod
    def convert_smd(path):
        try: smd = SMDReader.generate(path)
        except Exception as e: 
            return None
        if isinstance(smd, SMDScene):
            try:
                joint_parents, joint_positions, skins = smd.transform()
                joint_names = smd.skeleton.names
                joint_positions = joint_positions.reshape(-1)
                vertices = smd.mesh.vertices.reshape(-1)
                normals = smd.mesh.normals.reshape(-1)
                triangles = smd.mesh.triangles.reshape(-1)
                mesh = (vertices, normals, triangles)
                skeleton = (joint_names, joint_positions, joint_parents)
                rigging = Rigging.create(*mesh, *skeleton, skins)
            except Exception as e:
                return None
            else: return []
        else: return []

    @staticmethod
    def convert_gltf(path):
        try: scenes = GLTF.generate(path)
        except Exception as e:
            return None
        scenes = [x for x in scenes if isinstance(x, GLTFScene)]
        result = []
        for scene in scenes:
            joint_positions = scene.joint_position.reshape(-1)
            joint_parents = scene.joint_parent
            skeleton = (scene.joint_name, joint_positions, joint_parents)
            vertices = scene.vertices.reshape(-1)
            normals = scene.normals.reshape(-1)
            triangles = scene.triangles.reshape(-1)
            mesh = (vertices, normals, triangles)
            rigging = Rigging.create(*mesh, *skeleton, scene.skins)
            result.append(rigging)
        return result 