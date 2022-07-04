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

def get_request(url, max_try_count = 10):
    try_index = 0
    while try_index < max_try_count:
        try_index += 1
        try: 
            request_result = requests.get(url, timeout = 3)
        except: 
            print(url, 'request error for no.', try_index)
            time.sleep(1)
            continue
        if request_result.status_code != requests.codes.ok:
            time.sleep(1)
            continue
        content = str(request_result.content)
        break
    if try_index >= max_try_count: raise Exception()
    return content