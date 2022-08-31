from collada import *

class HelpReader:
    def __init__(self, content):
        self.content = content
    
    def read(self):
        return self.content

def find(string, substring, start = 0, step = 1):
    end = len(string) if step == 1 else None
    if step == -1: 
        substring = substring[len(substring) - 1::-1]
    substring = substring.encode('utf-8')
    index = string[start:end:step].find(substring)
    if index == -1: return -1
    elif step == 1: return start + index
    else: return start - index - len(substring) + 1

class Fixer:
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
    def remove_empty_diffuse(content):
        pattern = '<diffuse />'
        while True:
            start = find(content, pattern)
            if start == -1: break
            content = content[:start] + content[start + len(pattern):]
        return content

    @staticmethod
    def add_empty_vertex_weight_index(content):
        while True:
            start = find(content, '<v/>')
            if start == -1: break
            number = find(content, '<', start + 1)
            if number == -1: break
            if number != find(content, '</vertex_weights>', start + 1): break
            number = find(content, '<vertex_weights', start - 1, -1)
            nstart = find(content, '="', number)
            nend = find(content, '"', nstart + 2)
            number = int(content[nstart + 2:nend])
            vend = find(content, '<', start - 1, -1)
            if vend == -1: break
            if vend != find(content, '</vcount>', start - 1, -1): break
            vstart = find(content, '<vcount>', start - 1, -1)
            counts = content[vstart + len(b'<vcount>'):vend].split(b' ')
            counts = [x for x in counts if x != b'']
            assert(len(counts) == number)
            assert(all([x == b'0' for x in counts]))
            counts = b''.join([b'1 ' for _ in counts])[:-1]
            indices = b''.join([b'-1 ' for _  in counts * 2])[:-1]
            content = content[:start] + b'<v>' + indices + b'</v>' + content[start + 4:]
            content = content[:vstart + len(b'<vcount>')] + counts + content[vend:]       
        return content

    @staticmethod
    def remove_nan_number(content):
        while True:
            symbol = '-1.#QNAN0'
            start = find(content, symbol)
            if start == -1: break
            content = content[:start] + b'-1.000000' + content[start + len(symbol):]
        return content

    @staticmethod
    def remove_empty_image(content):
        start = -1
        while True:
            start = find(content, '<image', start + 1)
            if start == -1: break
            end = find(content, '>', start) + 1
            if content[end - 2:end] == b'/>':
                content = content[:start] + content[end:]
        return content

    @staticmethod
    def remove_broken_material(content, url):
        while True:
            start = find(content, 'target=' + url)
            if start == -1: break
            start = find(content, '<', start, -1)
            symbol = b'<instance_material'
            if content[start:start + len(symbol)] != symbol: break
            end = find(content, '>', start) + 1
            if content[end-2:end] != b'/>':
                end = find(content, '</instance_material>', start) + 1
                end += len(b'</instance_material>')
            content = content[:start] + content[end:]
        return content

    @staticmethod
    def remove_missing_image(content, surface):
        while True:
            start = find(content, surface)
            if start == -1: break
            pstart = find(content, '<newparam', start, -1)
            pend = find(content, '</newparam>', pstart) + len(b'</newparam>')
            if pstart < start and start < pend:
                content = content[:pstart] + content[pend:]
        return content

    @staticmethod
    def remove_missing_samlper(content, sampler):
        while True:
            start = find(content, sampler)
            if start == -1: break
            start = find(content, '<', start, -1)
            if content[start:start + len(b'<texture')] != b'<texture': break
            end = find(content, '>', start) + 1
            if content[end - 2:end] != b'/>':
                end = find(content, '</texture>', start) + len(b'</texture>')
            content = content[:start] + content[end:]
        return content

    @staticmethod
    def remove_broken_ref(content):
        urls, surfaces, samplers = set(), set(), set()
        while True:
            url, surface, sampler = None, None, None
            try: Collada(HelpReader(content))
            except Exception as e:
                if isinstance(e, DaeBrokenRefError):
                    msg = e.msg.split(' ')
                    if len(msg) == 4 and msg[0] == 'Material' \
                        and msg[2] == 'not' and msg[3] == 'found':
                        url = '"' + msg[1] + '"'
                    elif len(msg) == 6 and msg[0] == 'Missing' and msg[1] == 'image' \
                        and msg[3] == 'in' and msg[4] == 'surface':
                        surface = msg[5][1:-1]
                elif isinstance(e, material.DaeMissingSampler2D):
                    msg = e.args[0].split(' ')
                    if len(msg) == 6 and msg[0] == 'Missing' and msg[1] == 'sampler' \
                        and msg[3] == 'in' and msg[4] == 'node':
                        sampler = msg[2]
            if url is not None and url not in urls:
                urls.add(url)
                content = Fixer.remove_broken_material(content, url)
            elif surface is not None and surface not in surfaces:
                surfaces.add(surface)
                content = Fixer.remove_missing_image(content, surface)
            elif sampler is not None and sampler not in samplers:
                samplers.add(sampler)
                content = Fixer.remove_missing_samlper(content, sampler)
            else: break
        return content
                
    @staticmethod
    def fix(file):
        if isinstance(file, str):
            with open(file, 'rb') as f:
                content = f.read()
        else: content = file
        origin = lambda x:x
        fix_funs = [origin, Fixer.change_version, Fixer.remove_ref, Fixer.remove_instance_image,
                    Fixer.remove_empty_diffuse, Fixer.add_empty_vertex_weight_index,
                    Fixer.remove_nan_number, Fixer.remove_empty_image, Fixer.remove_broken_ref]
        origin_content = bytes([x for x in content])
        for i in range(2 * len(fix_funs)):
            exceptions = []
            for fix_fun in fix_funs:
                try: Collada(HelpReader(fix_fun(bytes([x for x in content]))))
                except Exception as e:
                    exceptions.append(e)
                else: return HelpReader(fix_fun(content))
            for j in range(1, len(exceptions)):
                if type(exceptions[j]) != type(exceptions[0]): 
                    content = fix_funs[j](content)
                elif isinstance(exceptions[0], DaeIncompleteError) and \
                    exceptions[0].msg != exceptions[j].msg:
                    content = fix_funs[j](content)
                else: continue
                break
        return HelpReader(origin_content)