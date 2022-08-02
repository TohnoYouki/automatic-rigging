import os
import sys
import json
sys.path.append('../../parse_tool/dae/')
from dae import DAE
sys.path.append('../../../utils/')
from multiprocess import multi_process

model_path = './unzip/'
save_path = './extract dae/'

def search_dae(path):
    result = []
    for subdir in os.listdir(path):
        if os.path.isdir(path + subdir):
            result.extend(search_dae(path + subdir + '/'))
        elif '.dae' in subdir.lower(): 
            result.append(path + subdir)
    return result

def get_pending():
    numbers = os.listdir(model_path)
    paths = [search_dae(model_path + x + '/') for x in numbers]
    paths = sum(paths, [])
    names = [path.split('/') for path in paths]
    names = ['dae' + '_' + x[-2] + '_' + x[-1].split('.')[0] for x in names]
    extracted = [x.split('.')[0] for x in os.listdir(save_path)]
    extracted = [x[:len(x) - x[::-1].index('_') - 1] for x in extracted]
    pending = [[paths[i], names[i]] for i in range(len(paths)) 
                if names[i] not in extracted]
    return pending

def extract(data):
    path, name = data
    try: 
        colladas = DAE.generate(path)
        if colladas is None:
            return [path, name, 'load_fail']
    except Exception as e: 
        return [path, name, 'parse_fail']
    if len(colladas) == 0: 
        return [path, name, 'zero']
    for j, collada in enumerate(colladas):
        collada.save(name + '_' + str(j), save_path)
    return [path, name, 'successful'] 

if __name__ == '__main__':
    process_number = 8
    pending = get_pending()

    status = multi_process(extract, pending, process_number)
    status = [x[1] for x in status]
    load_fail = [[x[0], x[1]] for x in status if x[2] == 'load_fail']
    parse_fail = [[x[0], x[1]] for x in status if x[2] == 'parse_fail']
    zero_fail = [[x[0], x[1]] for x in status if x[2] == 'zero']

    with open('parse_dae_result.json', 'w') as file:
        result = json.dumps({'load_fail': load_fail, 
                             'parse_fail': parse_fail, 
                             'zero_fail': zero_fail})
        file.write(result)

    load_fail.extend(parse_fail)
    load_fail.extend(zero_fail)
    fail = [x for x, y in load_fail]
    pending = get_pending()

    if len(pending) != len(fail) or any([x[0] not in fail for x in pending]): 
        print('please run again!')