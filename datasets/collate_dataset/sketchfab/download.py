import os
import json
import requests
from requests.exceptions import RequestException

save_dir = 'downloaded models/'
API_TOKEN = 'Put Your API Token Here'

def download(uid, name):
    headers = {'Authorization': 'Token {}'.format(API_TOKEN)}
    url = 'https://api.sketchfab.com/v3/models/{}/download'.format(uid)
    try:
        response = requests.get(url, headers = headers)
    except RequestException as exc:
        return f'An API Error Occured: {exc}'
    else:
        data = response.json()
        if 'glb' in data:
            file_type = 'glb'
            download_url = data['glb']['url']
        elif 'gltf' in data:
            file_type = 'zip'
            download_url = data['gltf']['url']
        elif 'detail' in data:
            return data['detail']
        else: return 'Unknown Failure'
        
    try: model = requests.get(download_url, stream = True)
    except Exception as exc: 
        return f'An Download Error Occured: {exc}'
    else:
        with open(save_dir + name + '.' + file_type, 'wb') as file:
            for chunk in model.iter_content(chunk_size = 128):
                file.write(chunk)
        return 'Download Successful'
        
if __name__ == '__main__':
    with open('download_info.json') as file:
        pending = json.load(file)
    downloaded = os.listdir(save_dir)
    for path in downloaded:
        uid = path.split('.')[0]
        if uid in pending: 
            pending[uid][2] = 'Download Successful'

    pass_keys = ['Download Successful', 'Not found.', 'Unknown Failure',
                 'You do not have permission to perform this action.']
    uids = [x for x in pending.keys() if pending[x][2] not in pass_keys]
    print(len(uids), 'Left')
    
    for i, uid in enumerate(uids):
        print(i)
        name, category, _ = pending[uid]
        pending[uid][2] = download(uid, uid)
        print(pending[uid][2])
        if pending[uid][2] == 'Too many requests.': break
        
        with open('download_info.json', 'w') as file:
            file.write(json.dumps(pending))
