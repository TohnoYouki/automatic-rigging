import os 
import json

path = 'search result/'
files = os.listdir(path)
uid_set = set()
uids, names, categories = [], [], []

for i in range(len(files)):
    with open(path + files[i]) as file:
        models = json.load(file)
    for model in models:
        if model['uid'] in uid_set: continue
        uid_set.add(model['uid'])
        uids.append(model['uid'])
        names.append(model['name'])
        categories.append([x['name'] for x in model['categories']])

if os.path.exists('download_info.json'):
    with open('download_info.json') as file:
        result = json.load(file)
else: result = {}

for i in range(len(uids)):
    if uids[i] not in result:
        result[uids[i]] = [names[i], categories[i], 'Not Try']

with open('download_info.json', 'w') as file:
    file.write(json.dumps(result))