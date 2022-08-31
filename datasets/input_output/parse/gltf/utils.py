import numpy as np

def calculate_vertex_normal(positions, triangles):
    normal_set = [[] for _ in range(len(positions))]
    triangles = np.array(triangles).reshape(-1, 3)
    for i in range(len(triangles)):
        x, y, z = triangles[i]
        x, y, z = map(lambda x: positions[x], (x, y, z))
        normal = np.cross(y - x, z - x)
        area = np.linalg.norm(normal)
        if np.linalg.norm(normal) < 1e-8:
            normal = [0, 1.0, 0]
        else: normal = normal / np.linalg.norm(normal)
        for j in triangles[i]:
            normal_set[j].append([normal, area])
    normals = np.ones(positions.shape)
    for i in range(len(normal_set)):
        if len(normal_set[i]) <= 0: continue
        normal = [x * weight for x, weight in normal_set[i]]
        normal = np.sum(normal, 0)
        if np.linalg.norm(normal) < 1e-8:
            normal = normal_set[i][0][0]
        if np.linalg.norm(normal) >= 1e-8:
            normals[i] = normal
    normals = normal / np.linalg.norm(normals, axis = 1)[:, np.newaxis]
    return normals

def convert_to_triangle(indices, mode):
    if mode == 0:
        indices = [[x, x, x] for x in indices]
    elif mode == 1:
        assert(len(indices) % 2 == 0)
        line = [[i, i + 1] for i in range(0, len(indices), 2)]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 2:
        line = [[i, (i + 1) % len(indices)] for i in range(len(indices))]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 3:
        line = [[i, i + 1] for i in range(len(indices) - 1)]
        indices = [[indices[x], indices[y], indices[x]] for x, y in line]
    elif mode == 4:
        assert(len(indices) % 3 == 0)
        indices = [[indices[i], indices[i + 1], indices[i + 2]]
                    for i in range(0, len(indices), 3)]
    elif mode == 5:
        assert(len(indices) >= 3)
        indices = [[indices[i], indices[i + 1], indices[i + 2]]
                    if i % 2 == 0 else 
                    [indices[i + 1], indices[i], indices[i + 2]] 
                    for i in range(0, indices - 2)]
    elif mode == 6:
        assert(len(indices) >= 3)
        indices = [[indices[0], indices[i - 1], indices[i]] 
                    for i in range(2, len(indices))]
    else: raise Exception('Unknown Primitive Mode!')
    indices = np.array(indices).reshape(-1)
    return indices