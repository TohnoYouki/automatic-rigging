from .scene import Scene
from pygltflib import GLTF2
from .node import parse_node
from .mesh import parse_mesh
from .skeleton import parse_skeleton
from .accessor import parse_accessor

class GLTF:
    @staticmethod
    def generate(path):
        if path.split('.')[-1] == 'gltf':
            gltf = GLTF2().load(path)
        elif path.split('.')[-1] == 'glb':
            gltf = GLTF2().load_binary(path)
        else: return []
        accessors = parse_accessor(gltf)
        meshes = parse_mesh(gltf, accessors)
        nodes = parse_node(gltf, meshes)
        skeletons = parse_skeleton(gltf, nodes, accessors)
        scenes = [Scene.parse(x, nodes) for x in gltf.scenes]
        return scenes