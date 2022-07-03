import os, json
from utils import find_all, load_temp_json, multi_process
from utils import base_url, formats, save_temp_json, get_request

def filter_format(number):
    models = load_temp_json(number)
    for i in range(len(models)):
        if i % 20 == 0: print(number, i, len(models))
        if len(models[i]) > 2: continue
        result = False
        url = base_url + models[i][0] + 'model/' + models[i][1]
        content = get_request(url)
        if content is None:
            print('process ', number, ' error')
            continue
        else: content = content.lower()
        for j in range(len(formats)):
            find_results = find_all(content, formats[j])
            if len(find_results) > 0: result = True
        models[i].append(result)
        if i % 100 == 0 or i == len(models) - 1:
            save_temp_json(number, models)

if __name__ == '__main__':
    process_number = 8
    with open('model_resource_sections.json') as file:
        games = json.load(file)

    if os.path.isfile('model_resource_models.json'):
        with open('model_resource_models.json') as file:
            models = json.load(file)
            finish = [(a, b) for a, b, _ in models]
    else:
        models, finish = [], []
        
    games = sum([games[x] for x in games], [])

    pedding, visited = [], set()
    for html, name, sections in games:
        for section_name in sections:
            for model in sections[section_name]:
                visited.add((html, model))
                if (html, model) in finish: continue
                pedding.append([html, model])
    models = [x for x in models if (x[0], x[1]) in visited]
    
    labeled = multi_process(filter_format, pedding, process_number)
    labeled = [x for x in labeled if len(x) > 2]
    models.extend(labeled)
    result = {}
    for html, number, label in models:
        if number in result: print(html, number)
        result[number] = [html, label]
    result = [[value[0], number, value[1]] for number, value in result.items()]
    result.sort(key = lambda x:x[1])
    with open('model_resource_models.json', 'w') as file:
        result = json.dumps(result)
        file.write(result)