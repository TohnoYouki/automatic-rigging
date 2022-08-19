import math
import time
import requests

formats = ['dae', 'smd']
base_url = 'https://www.models-resource.com/'

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

def split_into_slices(array, size):
    number = len(array) // size
    if number * size < len(array): number += 1
    start = [i * size for i in range(number)]
    end = [min((i + 1) * size, len(array)) for i in range(number)]
    slices = [array[start[i]:end[i]] for i in range(number)]
    return slices

def get_request(url, max_try_count = 10, **kargs):
    try_index = 0
    while try_index < max_try_count:
        try_index += 1
        try: 
            request_result = requests.get(url, timeout = 3, **kargs)
        except: 
            print(url, 'request error for no.', try_index)
            time.sleep(1)
            continue
        if request_result.status_code != requests.codes.ok:
            time.sleep(1)
            continue
        break
    if try_index >= max_try_count: raise Exception()
    return request_result