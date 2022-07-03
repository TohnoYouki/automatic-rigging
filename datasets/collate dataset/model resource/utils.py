import os
import json
import time
import requests
from multiprocessing import Pool

formats = ['dae', 'smd']
base_url = 'https://www.models-resource.com/'
temp_path = './temp/{}.json'

def find_middle_content(string, start, end):
    start = string.find(start) + len(start)
    end = string[start:].find(end) + start
    return string[start:end]

def find_all(string, content):
    result, index = [], 0
    while True:
        index = string.find(content, index)
        if index != -1:
            result.append(index)
            index += 1
        else: break
    return result

def get_request(url, max_try_count = 10):
    try_index = 0
    while try_index < max_try_count:
        try_index += 1
        try: content = str(requests.get(url).content)
        except: 
            print(url, 'request error for no.', try_index)
            time.sleep(1)
            continue
        break
    if try_index >= max_try_count: return None
    return content

def remove_temp_json(number):
    os.remove(temp_path.format(number))

def load_temp_json(number):
    path = temp_path.format(number)
    with open(path) as file:
        content = json.load(file)
    return content

def save_temp_json(number, content):
    path = temp_path.format(number)
    with open(path, 'w') as file:
        content = json.dumps(content)
        file.write(content)

def multi_process(fun, data, number):
    params = [data[i::number] for i in range(number)]
    for i in range(number): 
        if not os.path.isfile(temp_path.format(i)):
            save_temp_json(i, params[i])
    pool = Pool(processes = number)
    pool.map(fun, range(number))
    result = [load_temp_json(i) for i in range(number)]
    for i in range(number): remove_temp_json(i)
    return sum(result, [])