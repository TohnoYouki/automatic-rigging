import numpy as np
from queue import Queue, PriorityQueue

class HuffmanUtil:
    @staticmethod
    def coding_to_numpy(coding):
        result = []
        coding += '0' * (8 - (len(coding) % 8))
        num = len(coding) // 8
        for i in range(num):
            result.append(int(coding[i * 8:i * 8 + 8], 2))
        return np.array(result).astype(np.uint8)

    @staticmethod
    def decode(keys, length, coding, number):
        result, key = [], 0
        keys = {(x, length[i]):i for i, x in enumerate(keys)}
        coding = [bin(x)[2:] for x in coding]
        coding = ''.join(['0' * (8 - len(x)) + x for x in coding])
        size = 0
        for c in coding:
            key = key * 2 + int(c)
            size += 1
            if (key, size) in keys:
                result.append(keys[(key, size)])
                key, size = 0, 0
        result = np.array(result[:number])
        return result

    @staticmethod
    def histogram(numbers, max_node):
        values = sorted(set(numbers))
        pdf = {x:0 for x in values}
        for number in numbers:
            pdf[number] += 1
        pdf = [[x, pdf[x]] for x in pdf]
        pdf = sorted(pdf, key = lambda x:x[1], reverse = True)
        if max_node < len(pdf):
            left_num = np.sum([x[1] for x in pdf[max_node:]])
            pdf = [pdf[i] for i in range(max_node - 1)]
            pdf.append([None, left_num])
        keys = [x[0] for x in pdf]
        frequences = [x[1] for x in pdf]
        return keys, frequences

    @staticmethod
    def build_huffman_dict(frequences):
        queue = PriorityQueue()
        parents = [-1 for _ in range(len(frequences))]
        for i, freq in enumerate(frequences):
            queue.put_nowait((freq, i))
        while queue.qsize() > 1:
            freq1, index1 = queue.get_nowait()
            freq2, index2 = queue.get_nowait()
            parents[index1] = len(parents)
            parents[index2] = len(parents)
            queue.put_nowait((freq1 + freq2, len(parents)))
            parents.append(-1)
        children = [[] for _ in range(len(parents))]
        for i, parent in enumerate(parents):
            if parent != -1:
                children[parent].append(i)
        queue = Queue()
        queue.put_nowait(len(children) - 1)
        values = ['' for _ in range(len(children))]
        while not queue.empty():
            index = queue.get_nowait()
            if len(children[index]) > 0:
                left, right = children[index]
                queue.put_nowait(left)
                queue.put_nowait(right)
                values[left] = values[index] + '0'
                values[right] = values[index] + '1'
        return values[:len(frequences)]

class FloatDiffGenerator():
    def __init__(self, bytes, step):
        self.bytes = bytes
        self.step = step
        self.cursor = 0

    def decode(self, predict):
        dtype = predict.dtype
        bytes = self.bytes[self.cursor:self.cursor + self.step]
        self.cursor += self.step
        predict = np.frombuffer(np.array([predict]).tobytes(), np.uint8)
        result = np.bitwise_xor(predict, bytes)
        result = np.frombuffer(result.tobytes(), dtype)[0]
        return result
        
class Huffman:
    @staticmethod
    def compress(numbers, max_node = 30):
        keys, frequences = HuffmanUtil.histogram(numbers, max_node)
        if len(frequences) == 1:
            return {'number': len(numbers), 'value': numbers[0]}
        key_coding = HuffmanUtil.build_huffman_dict(frequences)
        dict_coding, none_coding = '', []
        for number in numbers:
            if number not in keys:
                none_coding.append(number)
                dict_coding += key_coding[keys.index(None)]
            else: dict_coding += key_coding[keys.index(number)]
        dict_coding = HuffmanUtil.coding_to_numpy(dict_coding)
        none_coding = np.array(none_coding)
        if keys[-1] is None: keys = keys[:-1]
        key_length = np.array([len(x) for x in key_coding])
        key_coding = np.array([int(x, 2) for x in key_coding])
        return {'key': np.array(keys), 
                'number': len(numbers), 
                'key_length': key_length,
                'key_coding': key_coding,
                'dict_coding': dict_coding, 
                'none_coding': none_coding}

    @staticmethod
    def compress_diff(numbers, max_node = 30):
        diff = np.concatenate((numbers[:1], numbers[1:] - numbers[:-1]))
        state_dict = Huffman.compress(diff, max_node)
        none_index = [i for i in range(len(numbers)) 
                      if diff[i] not in state_dict['key']]
        assert(len(none_index) == len(state_dict['none_coding']))
        none_number = [numbers[x] for x in none_index]
        state_dict['none_coding'] = np.array(none_number)
        return state_dict

    @staticmethod
    def decompress(state_dict):
        result = []
        num = state_dict['number']
        if 'key' not in state_dict:
            return np.array([state_dict['value'] for _ in range(num)])
        keys = state_dict['key']
        key_length = state_dict['key_length']
        key_coding = state_dict['key_coding']
        dict_coding = state_dict['dict_coding']
        none_coding = state_dict['none_coding']
        indices = HuffmanUtil.decode(key_coding, key_length, dict_coding, num)
        none_cursor = 0
        for index in indices:
            if index >= len(keys):
                result.append(none_coding[none_cursor])
                none_cursor += 1
            else: result.append(keys[index])
        return np.array(result), indices

    @staticmethod
    def decompress_diff(state_dict):
        result = []
        diff, indices = Huffman.decompress(state_dict)
        keys = state_dict['key']
        for i in range(len(diff)):
            if i > 0 and indices[i] < len(keys):
                result.append(result[-1] + diff[i])
            else: result.append(diff[i])
        return np.array(result)