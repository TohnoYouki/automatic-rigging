import os
import json
import requests
import itertools
from requests.exceptions import RequestException

def collate_all_models(format_url):
    result, count, max_number = [], 24, 10000
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
                if count <= 0: return result
                next_url = format_url.format(count, len(result))
            else: result.extend(request_result)
            if next_url is None: return result
    return None

def parse(slug, min_face, max_face):
    format_url = 'https://api.sketchfab.com/v3/search?archives_flavours=false&'
    format_url += 'categories={}&count={}&cursor={}&downloadable=true&{}{}'
    format_url += 'rigged=true&sort_by=publishedAt&type=models'
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

number = 0
for i in range(len(progress)):
    if progress[i][2]: continue
    slug, face_range = progress[i][:2]
    min_face, max_face = face_range
    url, name = parse(slug, min_face, max_face)
    collate_result = collate_all_models(url)
    if collate_result is None:
        raise Exception('There is something wrong when collating info!')
    with open('search result/' + name + '.json', 'w') as file:
        file.write(json.dumps(collate_result))
    progress[i][2] = True
    with open('progress.json', 'w') as file:
        file.write(json.dumps(progress))