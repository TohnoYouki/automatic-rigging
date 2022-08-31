import numpy as np
from .parse import *
from .basic import *

class SceneConverter:
    @staticmethod
    def convert(file, format):
        try:
            if format == 'dae':
                result = SceneConverter.convert_dae(file)
            elif format == 'smd':
                result = SceneConverter.convert_smd(file)
            elif format == 'gltf' or format == 'glb':
                result = SceneConverter.convert_gltf(file)
            else: result = None
        except Exception as e:
            result = None
        return result 

    @staticmethod
    def convert_dae(file):
        scenes = DAE.generate(file)
        if scenes is None: return None
        result = []
        for scene in scenes:
            riggings, scene_skeletons = [], []
            for skeleton in scene.skeletons:
                names = skeleton.names
                positions = skeleton.positions
                parents = skeleton.parents
                matrixs = [np.identity(4) for x in range(len(names))]
                skeleton = Skeleton(names, positions, parents, matrixs)
                scene_skeletons.append(skeleton)
            for i, mesh in enumerate(scene.meshes):
                skin = Skin.from_vertex_skins(mesh.skins)
                mesh = Mesh(mesh.vertices, mesh.normals, mesh.triangles)
                riggings.append(Rigging(mesh, scene.refs[i], skin))
            matrixs = np.concatenate([x[None] for x in scene.matrixs])
            result.append(Scene(riggings, scene_skeletons, matrixs))
        return result

    @staticmethod
    def convert_smd(file):
        smd = SMDReader.generate(file)
        if isinstance(smd, SMDScene):
            parents, positions, skins = smd.transform()
            skins = Skin.from_vertex_skins(skins)
            names = smd.skeleton.names
            mesh = Mesh(smd.mesh.vertices, smd.mesh.normals, smd.mesh.triangles)
            matrixs = np.array([np.identity(4) for _ in range(len(names))])
            skeleton = Skeleton(names, positions, parents, matrixs)
            rigging = Rigging(mesh, 0, skins)
            return [Scene([rigging], [skeleton], np.identity(4))]
        if isinstance(smd, SMDVertexAnimation): 
            smd = smd.mesh
        if isinstance(smd, SMDStaticMesh):
            mesh = Mesh(smd.vertices, smd.normals, smd.triangles)
            skins = [[] for _ in range(len(smd.vertices))]
            skins = Skin.from_vertex_skins(skins)
            return [Scene([Rigging(mesh, None, skins)], [], np.identity(4))]
        return []

    @staticmethod
    def convert_gltf(file):
        scenes = GLTF.generate(file)
        scenes = [x for x in scenes if isinstance(x, GLTFScene)]
        result = []
        for scene in scenes:
            riggings, scene_skeletons = [], []
            for skeleton in scene.skeletons:
                names = skeleton.names
                positions = skeleton.positions
                parents = skeleton.parents
                matrixs = skeleton.joint_matrixs
                skeleton = Skeleton(names, positions, parents, matrixs)
                scene_skeletons.append(skeleton)
            for i, mesh in enumerate(scene.meshes):
                skin = Skin.from_vertex_skins(mesh.skins)
                skin.inverse_bind_matrixs = scene.inverse_bind_matrixs[i]
                mesh = Mesh(mesh.vertices, mesh.normals, mesh.triangles)
                riggings.append(Rigging(mesh, scene.skeleton_ref[i], skin))
            matrixs = np.concatenate([x[None] for x in scene.matrixs]) 
            result.append(Scene(riggings, scene_skeletons, matrixs))
        return result