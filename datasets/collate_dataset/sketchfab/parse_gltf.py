import os
import sys
import json
sys.path.append('../../parse_tool/gltf/')
from gltf import GLTF
from scene import Scene
sys.path.append('../../../utils/')
from multiprocess import multi_process

model_dir = 'downloaded models/'
save_dir = 'extract models/'

def get_pending():
    models = os.listdir(model_dir)
    extracted = os.listdir(save_dir)
    extracted = set([x.split('_')[0] for x in extracted])
    models = [x for x in models if x.split('.')[0] not in extracted]
    return models

def extract(data):
    path = data
    name = path.split('.')[0]
    try: scenes = GLTF.generate(model_dir + path)
    except Exception as e:
        return [path, 'parse fail']
    scenes = [x for x in scenes if isinstance(x, Scene)]
    if len(scenes) == 0:
        return [path, 'zero fail']
    for i, scene in enumerate(scenes):
        scene.save(name + '_' + str(i), save_dir)
    return [path, 'successful']

if __name__ == '__main__':
    process_number = 6
    models = get_pending()
    status = multi_process(extract, models, process_number)

    status = [x[1] for x in status]
    parse_fail = [x[0] for x in status if x[1] == 'parse fail']
    zero_fail = [x[0] for x in status if x[1] == 'zero fail']
    with open('parse_gltf_result.json', 'w') as file:
        result = {'parse_fail': parse_fail, 'zero_fail': zero_fail}
        file.write(json.dumps(result))
    fail = parse_fail + zero_fail

    models = get_pending()
    if len(models) != len(fail) or any([x not in fail for x in models]):
        print('please run again!')
