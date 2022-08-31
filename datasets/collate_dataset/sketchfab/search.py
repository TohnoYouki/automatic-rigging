import os
import json
import time
import requests
import itertools
from requests.exceptions import RequestException

def collate_all_models(format_url, max_number):
    result, count = [], 24
    while len(result) < max_number:
        print(len(result))
        url = format_url.format(count, len(result))
        assert(len(result) == 0 or url == next_url)
        try: response = requests.get(url)
        except RequestException as exc:
            print(f'An API error occured: {exc}')
            return None
        else:
            data = response.json()
            if 'detail' in data: 
                print(data['detail'])
                return None
            next_url = data['next']
            request_result = data['results']
            if len(request_result) < count:
                count = count // 2
                if count <= 0: return None, result
                next_url = format_url.format(count, len(result))
            else: result.extend(request_result)
            if next_url is None: return None, result
    return next_url, result

def parse(slug, min_face, max_face):
    format_url = 'https://api.sketchfab.com/v3/search?archives_flavours=false&'
    format_url += 'categories={}&count={}&cursor={}&downloadable=true&{}{}'
    format_url += 'rigged=true&sort_by=-publishedAt&type=models'
    name = slug + '-' + str(0 if min_face is None else min_face)
    name += '-' + ('None' if max_face is None else str(max_face))
    if min_face is not None:
        min_face = 'min_face_count={}&'.format(min_face)
    else: min_face = ''
    if max_face is not None:
        max_face = 'max_face_count={}&'.format(max_face) 
    else: max_face = ''
    url = format_url.format(slug, {}, {}, max_face, min_face)
    return url, name

def initial_progress():
    with open('type.json') as file:
        types = json.load(file)
    face_count_levels = [[None, 4000], [4000, 8000], [8000, 12000], 
                         [12000, 20000], [20000, 30000], [30000, None]]
    progress = [[x, y, False] for x, y in 
        itertools.product([x['slug'] for x in types], face_count_levels)]
    if os.path.exists('progress.json'):
        with open('progress.json') as file:
            last_progress = json.load(file)
        if not all([x[2] for x in last_progress]):
            progress = last_progress
    with open('progress.json', 'w') as file:
        file.write(json.dumps(progress))
    return progress

def collate_from_last(url, last_result):
    parse_time = lambda x: time.strptime(x['publishedAt'].split('.')[0], 
                                         '%Y-%m-%dT%H:%M:%S')
    if len(last_result) > 0:
        last_time = sorted([parse_time(x) for x in last_result])[-1]
    else: last_time = None
    result = last_result
    step, max_number = 24, 10000
    for i in range(0, max_number, step):
        url, temps = collate_all_models(url, step)
        result.extend(temps)
        if url is None: break 
        oldest = parse_time(result[-1])
        if last_time is not None or oldest < last_time: break
    indices, uid_set = [False for _ in range(len(result))], set()
    for i in range(len(indices)):
        if result[i]['uid'] not in uid_set:
            uid_set.add(result[i]['uid'])
            indices[i] = True
    result = [result[i] for i, x in enumerate(indices) if x]
    result = sorted(result, key = parse_time)
    return result

update_from_last = True
progress = initial_progress()
for i in range(len(progress)):
    if progress[i][2]: continue
    slug, (min_face, max_face) = progress[i][:2]
    url, name = parse(slug, min_face, max_face)
    print(name)
    file_path = 'search result/' + name + '.json'
    if update_from_last and os.path.exists(file_path):
        with open(file_path) as file:
            last_result = json.load(file)
    else: last_result = []
    result = collate_from_last(url, last_result)
    if result is None:
        raise Exception('There is something wrong when collating info!')
    with open(file_path, 'w') as file:
        file.write(json.dumps(result))
    progress[i][2] = True
    with open('progress.json', 'w') as file:
        file.write(json.dumps(progress))