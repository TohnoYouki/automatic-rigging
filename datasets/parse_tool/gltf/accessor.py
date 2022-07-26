import struct
import numpy as np
from operator import mul
from pygltflib import GLTF2
from functools import reduce

def parse_buffers(gltf):
    result = []
    for buffer in gltf.buffers:
        data = gltf.get_data_from_buffer_uri(buffer.uri)
        result.append(data[:buffer.byteLength])
    return result

def parse_bufferviews(gltf):
    buffers = parse_buffers(gltf)
    result = []
    for view in gltf.bufferViews:
        data, stride = buffers[view.buffer], view.byteStride
        offset, length = view.byteOffset, view.byteLength
        data = data[offset:offset + length]
        result.append([data, stride])
    return result          

def data_shape(type):
    if type == 'SCALAR': 
        shape = [1]
    elif 'VEC' == type[:3] and len(type) == 4:
        shape = [int(type[-1])]
    elif 'MAT' == type[:3] and len(type) == 4:
        shape = [int(type[-1]), int(type[-1])] 
    else: raise Exception('Unknown Data Shape!')
    return shape

def data_type(type):
    if type == 5120:
        return 'b', 1
    elif type == 5121:
        return 'B', 1
    elif type == 5122:
        return 'h', 2
    elif type == 5123:
        return 'H', 2
    elif type == 5125:
        return 'I', 4
    elif type == 5126:
        return 'f', 4
    else: raise Exception('Unknown Data Type!')

def pick_data_from_bufferview(data, stride, offset, count, type, shape):
    raw, result = data[offset:], []
    shape = data_shape(shape)
    number = reduce(mul, shape, 1)
    type, dsize = data_type(type)
    csize = number * dsize
    for i in range(count):
        if stride is not None:
            result.append(raw[i * stride:i * stride + csize])
        else: result.append(raw[i * csize:(i + 1) * csize])
    result = [[x[i * dsize:(i + 1) * dsize] 
               for i in range(number)] for x in result]
    result = [[struct.unpack(type, x)[0] for x in y] for y in result]
    result = np.array(result).reshape(count, *shape)
    return result

def parse_sparse(buffer_views, accessor):
    sparse = accessor.sparse
    count = sparse.count
    indices = sparse.indices
    view = buffer_views[indices.bufferView]
    type = indices.componentType
    assert(type in [5121, 5123, 5125])
    params = (*view, indices.byteOffset, count, type, 'SCALAR')
    indices = pick_data_from_bufferview(*params).reshape(-1)
    data_view = buffer_views[sparse.values.bufferView]
    offset = sparse.values.byteOffset
    type, shape = accessor.componentType, accessor.type
    params = (*data_view, offset, count, type, shape)
    data = pick_data_from_bufferview(*params)
    assert(len(indices) == len(data))
    return indices, data

def parse_accessor(gltf):
    result = []
    buffer_views = parse_bufferviews(gltf)
    assert(isinstance(gltf, GLTF2))
    for accessor in gltf.accessors:
        view = buffer_views[accessor.bufferView]
        offset, count = accessor.byteOffset, accessor.count
        type, shape = accessor.componentType, accessor.type
        params = (*view, offset, count, type, shape)
        data = pick_data_from_bufferview(*params)
        if accessor.sparse is not None:
            indices, sparse_data = parse_sparse(buffer_views, accessor)
            data[indices] = sparse_data
        result.append(data)
    return result