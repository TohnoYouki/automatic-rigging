import os
import sys
import json
sys.path.append('../../../utils/')
from multiprocess import multi_process
sys.path.append('../../')
from input_output.convert import SceneConverter

model_dir = './download models/'
save_dir = './extract/'

def get_pending():
    models = os.listdir(model_dir)
    extracted = os.listdir(save_dir)
    extracted = set([x.split('_')[0] for x in extracted])
    models = [x for x in models if x.split('.')[0] not in extracted]
    return models

def extract(data, lock):
    path = os.path.join(model_dir, data)
    result = SceneConverter.convert(path, 'glb')
    if result is None: return [data, 'parse failed']
    elif len(result) == 0: return [data, 'zero failed']
    for i, scene in enumerate(result):
        name = data.split('.')[0] + '_' + str(i)
        scene.save(save_dir, name)
    return [data, 'successful']

if __name__ == '__main__':
    process_number = 8
    models = get_pending()
    status, errors = multi_process(extract, models, process_number)

    failed = [x[1] for x in status if x[1][1] != 'successful']
    with open('parse_result.json', 'w') as file:
        file.write(json.dumps(failed))

    models = get_pending()
    failed = [x[0] for x in failed]
    if len(models) != len(failed) or len(errors) > 0 or \
        any([x not in failed for x in models]):
        print('please run again!')
