import os
import sys
import json
import requests
sys.path.append('../../../utils/')
from multiprocess import multi_process

save_dir = './zip/'

def download(data):
    result = []
    url, index = data
    download_url = 'https://www.models-resource.com/download/' + index + '/'
    model = requests.get(download_url, stream = True)
    for chunk in model.iter_content(chunk_size=128):
        result.append(chunk)
    return [index, result]

def save_models(datas):
    for index, data in datas:
        name, content = data
        if os.path.exists(save_dir + name + '.zip'): 
            os.remove(save_dir + name + '.zip')  
        with open(save_dir + name + '.zip', 'wb') as file:
            for chunk in content: 
                file.write(chunk)

def get_downloading():
    with open('section_label.json') as file:
        download_info = json.load(file)
    download_info = [x for x in download_info if x[2]]
    downloaded = {x.split('.')[0] for x in os.listdir(save_dir)}
    downloading = [[a, b] for a, b, c in download_info if b not in downloaded]
    return downloading

if __name__ == '__main__':
    process_number = 8
    downloading = get_downloading()
    multi_process(download, downloading, process_number, save = save_models)
    downloading = get_downloading()
    if len(downloading) > 0: print('please run again!')