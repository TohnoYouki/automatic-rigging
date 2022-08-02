import os, sys, json
sys.path.append('../../../utils/')
from multiprocess import multi_process
from utils import find_all, base_url, formats, get_request

def load_data():
    if os.path.isfile('models.json'):
        with open('models.json') as file:
            models = json.load(file)
            models = {(x, y): z for x, y, z in models}
    else: models = {}
    return models

def write_data(models):
    models = [[*x, models[x]] for x in models]
    with open('models.json', 'w') as file:
        file.write(json.dumps(models))

def filter_format(data):
    url, name = data
    result = False
    content = get_request(base_url + url + 'model/' + name).lower()
    for j in range(len(formats)):
        find_results = find_all(content, formats[j])
        if len(find_results) > 0: result = True
    return [url, name, result]

def save_models(datas):
    models = load_data()
    for index, data in datas:
        url, name, result = data
        models[(url, name)] = result
    write_data(models)

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
    write_data(models)
    pedding = [x for x in models if models[x] is None]
    return pedding  

if __name__ == '__main__':
    process_number = 8
    pedding = get_pending()
    multi_process(filter_format, pedding, 
                  process_number, save = save_models)
    pedding = get_pending()
    if len(pedding) > 0: print('please run again!')