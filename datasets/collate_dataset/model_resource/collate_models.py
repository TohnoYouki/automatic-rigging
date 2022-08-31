import os, sys, json
sys.path.append('../../../utils/')
from multiprocess import multi_process
from utils import find_all, base_url, formats
from utils import get_request, split_into_slices

def load_data():
    if os.path.isfile('models.json'):
        with open('models.json') as file:
            models = json.load(file)
            models = {(x, y): z for x, y, z in models}
    else: models = {}
    return models

def filter_format(datas, lock):
    result = []
    for data in datas:
        url, name = data
        flag = False
        content = get_request(base_url + url + 'model/' + name)
        content = str(content.content).lower()
        for j in range(len(formats)):
            find_results = find_all(content, formats[j])
            if len(find_results) > 0: flag = True
        result.append([url, name, flag])
    lock.acquire()
    models = load_data()
    for url, name, flag in result:
        models[(url, name)] = flag
    models = [[*x, models[x]] for x in models]
    with open('models.json', 'w') as file:
        file.write(json.dumps(models))
    lock.release()
    return [url, name, result]

def get_pending():
    with open('section.json') as file:
        sections = json.load(file)
    models = {}
    for section in sections:
        for model in section[-1]:
            models[(section[1], model)] = None
    last_models = load_data()
    for key in models.keys():
        if key in last_models:
            models[key] = last_models[key]
    models = [[*x, models[x]] for x in models]
    with open('models.json', 'w') as file:
        file.write(json.dumps(models))
    pedding = [[x, y] for x, y, z in models if z is None]
    return pedding  

if __name__ == '__main__':
    process_number = 8
    pedding = get_pending()
    print(len(pedding), 'left')
    slice_size = max(1, min(len(pedding) // process_number, 50))
    pedding = split_into_slices(pedding, slice_size)
    _, errors = multi_process(filter_format, pedding, process_number)
    pedding = get_pending()
    if len(pedding) > 0 or len(errors) > 0: print('please run again!')