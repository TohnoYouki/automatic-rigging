import numpy as np

def unit_vectors_to_oct(vectors):
    denominator = np.sum(np.abs(vectors), axis = 1)
    result = (vectors[:, :2] / denominator[:, None]).copy()
    negative = vectors[:, 2] <= 0.0
    sign = -np.ones(result.shape)
    sign[result >= 0.0] = 1.0
    result[negative] = 1.0 - np.abs(result[negative])[:, [1, 0]]
    result[negative] *= sign[negative]
    return result

def oct_to_unit_vectors(vectors):
    z = 1.0 - np.abs(vectors[:, 0]) - np.abs(vectors[:, 1])
    result = np.concatenate((vectors[:, :2], z[:, None]), axis = 1)
    negative = z < 0
    sign = -np.ones((len(result), 2))
    sign[result[:, :2] >= 0.0] = 1.0
    result[negative, :2] = 1.0 - np.abs(result[negative][:, [1, 0]])
    result[negative, :2] *= sign[negative]
    result = result / np.linalg.norm(result, axis = 1)[:, None]
    return result

def adjust_integer(numbers):
    if len(numbers) == 0: return numbers
    max_number = np.max(numbers)
    min_number = np.min(numbers)
    if min_number >= -128 and max_number < 128:
        return numbers.astype(np.int8)
    elif min_number >= 0 and max_number < 256:
        return numbers.astype(np.uint8)
    elif min_number >= -32768 and max_number < 32768:
        return numbers.astype(np.int16)
    elif min_number >= 0 and max_number < 65536:
        return numbers.astype(np.uint16)
    elif min_number >= -2147483648 and max_number < 2147483648:
        return numbers.astype(np.int32)
    elif min_number >= 0 and max_number < 4294967296:
        return numbers.astype(np.uint32)
    else: return numbers