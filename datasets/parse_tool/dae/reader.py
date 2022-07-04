from collada import *

def find(string, substring, start = 0, step = 1):
    end = len(string) if step == 1 else None
    if step == -1: 
        substring = substring[len(substring) - 1::-1]
    substring = substring.encode('utf-8')
    index = string[start:end:step].find(substring)
    if index == -1: return -1
    elif step == 1: return start + index
    else: return start - index - len(substring) + 1

class Reader:
    def __init__(self, content):
        self.content = content

    def read(self): return self.content
    
    @staticmethod
    def change_version(content):
        index = find(content, 'COLLADA')
        assert(index != -1)
        end = find(content, '>', index) + 1
        head = '<?xml version="1.0" encoding="utf-8"?>\n'
        head += '<COLLADA xmlns='
        head += '"http://www.collada.org/2005/11/COLLADASchema"'
        head += ' version="1.4.1">'
        content = head.encode('utf-8') + content[end:]
        return content

    @staticmethod
    def remove_ref(content):
        while True:
            ref_start = find(content, '<ref>')
            ref_end = find(content, '</ref>')
            if ref_start == -1: break
            start = find(content, '>', ref_start - 1, -1)
            end = find(content, '<', ref_end + 1)
            assert(content[start - 9:start] == 'init_from'.encode('utf-8'))
            ref_content = content[ref_start + 5:ref_end]
            content = content[:start + 1] + ref_content + content[end:]
        return content

    @staticmethod
    def remove_instance_image(content):
        i_start = -1
        while True:
            i_start = find(content, '<instance_image', i_start + 1)
            if i_start == -1: break
            start = find(content, 'sampler2D', i_start - 1, -1)
            sample2D = '<sampler2D>'.encode('utf-8')
            if content[start - 1:start + 10] != sample2D: continue
            end = find(content, '</sampler2D>', start)
            assert(end != -1)
            if find(content[start:end], 'source') != -1: continue
            start = find(content, 'newparam', i_start - 1, -1)
            newparam = '<newparam'.encode('utf-8')
            if content[start - 1:start + 8] != newparam: continue
            i_end = find(content, '>', i_start + 1) + 1
            number = start - find(content, '\n', start - 1, -1) - 2
            start = find(content, 'sid="', start) + 5
            end = find(content, '"', start)
            surface = content[start:end] + '-surface'.encode('utf-8')
            start = find(content, 'url="', i_start) + 6
            end = find(content, '"', start)
            url = content[start:end]
            instance = '<source>'.encode('utf-8') + surface
            instance += '</source>'.encode('utf-8')
            newparam1 = '<newparam sid="'
            newparam2 = '">\n' + (number + 1) * '\t' + '<surface type="2D">\n'
            newparam2 += (number + 2) * '\t' + '<init_from>'
            newparam3 = '</init_from>\n' + (number + 1) * '\t' + '</surface>\n'
            newparam3 += number * '\t' + '</newparam>\n' + number * '\t'
            newparam = newparam1.encode('utf-8') + surface
            newparam = newparam + newparam2.encode('utf-8') + url
            newparam = newparam + newparam3.encode('utf-8')
            start = find(content, '<newparam', i_start - 1, -1)
            prev_content = content[:start] + newparam + content[start:i_start] + instance
            i_start = len(prev_content)
            content = prev_content + content[i_end:]
        return content

    @staticmethod
    def load(path):
        with open(path, 'rb') as file:
            content = file.read()
        content = Reader.change_version(content)
        content = Reader.remove_ref(content)
        content = Reader.remove_instance_image(content)
        ignore_errors = [common.DaeIncompleteError, common.DaeBrokenRefError]
        try: collada = Collada(Reader(content), ignore = ignore_errors)
        except Exception as e: return None
        return collada