import re
from .static_mesh import StaticMesh
from .rigging_mesh import RiggingMesh
from .vertex_animation import VertexAnimation
from .skeletal_animation import SkeletalAnimation

class SMDReader:
    @staticmethod
    def remove_comment(content):
        result = []
        for i in range(len(content)):
            for j, text in enumerate(content[i]):
                index = text.find('//')
                if index >= 0: 
                    content[i] = content[i][:j + 1]
                    content[i][-1] = content[i][-1][:index]
                    break
            content[i] = [x for x in content[i] if len(x) > 0]
            if len(content[i]) > 0 or index < 0:
                result.append(content[i])
        return result

    @staticmethod
    def parse_block(content):
        content = SMDReader.remove_comment(content)
        result = {'nodes': None, 'skeleton': None, 
                  'triangles': None, 'vertexanimation': None}
        for i in range(len(content)):
            if len(content[i]) <= 0: continue
            if content[i][0] == 'version' and content[i][1] == '1': break
        if len(content) == 0 or i >= len(content): return result
        content = content[i + 1:]
        now_block = None
        for i in range(len(content) + 1):
            if i < len(content):
                if len(content[i]) > 0 and content[i][0] in result and now_block is None:
                    now_block = [content[i][0], i]
            if now_block is None: continue
            if i == len(content) or (len(content[i]) > 0 and content[i][0] == 'end'):
                result[now_block[0]] = content[now_block[1] + 1:i]
                now_block = None
        assert(result['nodes'] is not None)
        assert(result['skeleton'] is not None)
        return result

    @staticmethod
    def generate(path):
        reg = re.compile("\s+") 
        with open(path, 'rb') as file:
            content = [line for line in file]
        content = [line.decode('ISO-8859-1') for line in content]
        content = [reg.split(line.strip()) for line in content]
        result = SMDReader.parse_block(content)
        params = (result['nodes'], result['skeleton'])
        skeleton = SkeletalAnimation.generate(*params)
        triangles = StaticMesh.generate(result['triangles'])
        vat = VertexAnimation.parse(result['vertexanimation'])
        if skeleton is None and triangles is None: return None
        assert(vat is None or triangles is not None)
        if skeleton is None and vat is None: return triangles
        if triangles is None: return skeleton
        if skeleton is None: return VertexAnimation.generate(triangles, vat)
        assert(vat is None)
        skeleton.remove_uncompiled_node()
        if RiggingMesh.check_correct(skeleton, triangles):
            return RiggingMesh.generate(skeleton, triangles)
        else: return triangles