from scene import Scene
from pygltflib import GLTF2
from skin import parse_skin
from node import parse_node
from mesh import parse_mesh
from accessor import parse_accessor

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
        skeletons = parse_skin(gltf, nodes, accessors)
        scenes = [Scene.parse(x, skeletons, nodes) for x in gltf.scenes]
        return scenes