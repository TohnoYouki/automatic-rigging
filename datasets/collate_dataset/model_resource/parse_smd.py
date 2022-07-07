import os
import json
from smd import SMDReader
from rigging_mesh import RiggingMesh
from multiprocess import multi_process

model_path = './unzip/'
save_path = './extract smd/'

def search_smd(path):
    result = []
    for subdir in os.listdir(path):
        if os.path.isdir(path + subdir):
            result.extend(search_smd(path + subdir + '/'))
        elif '.smd' in subdir.lower(): 
            result.append(path + subdir)
    return result

def extract(data):
    path, name = data
    try: 
        smd = SMDReader.generate(path)
    except Exception as e: 
        return [path, name, 'parse_fail']
    if isinstance(smd, RiggingMesh):
        try:
            smd.save(name, save_path)
        except Exception as e:
            return [path, name, 'save_fail']
    else: return [path, name, 'no_save_action']
    return [path, name, 'successful'] 

def get_pending():
    numbers = os.listdir(model_path)
    paths = sum([search_smd(model_path + number + '/') for number in numbers], [])
    names = [path.split('/') for path in paths]
    names = ['smd' + '_' + x[-2] + '_' + x[-1].split('.')[0] for x in names]
    extracted = [x.split('.')[0] for x in os.listdir(save_path)]
    pending = [[paths[i], names[i]] for i in range(len(paths)) 
                if names[i] not in extracted]
    return pending

if __name__ == '__main__':
    process_number = 8
    pending = get_pending()

    status = multi_process(extract, pending, process_number)
    status = [x[1] for x in status]
    fail_key = ['parse_fail', 'no_save_action', 'save_fail']
    failed = {x:[[y[0], y[1]] for y in status if y[2] == x] for x in fail_key}

    with open('parse_smd_result.json', 'w') as file:
        result = json.dumps(failed)
        file.write(result)
    
    failed = sum([failed[x] for x in failed], [])
    failed = [x[0] for x in failed]
    pending = get_pending()

    if len(pending) != len(failed) or any([x[0] not in failed for x in pending]): 
        print('please run again!') 
