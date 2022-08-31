import os
import sys
import json
from utils import get_request
sys.path.append('../../../utils/')
from multiprocess import multi_process

save_dir = './zip/'

def download(data, lock):
    url, index = data
    download_url = 'https://www.models-resource.com/download/' + index + '/'
    model = get_request(download_url, 10)
    if os.path.exists(save_dir + index + '.zip'):
        os.remove(save_dir + index + '.zip')
    with open(save_dir + index + '.zip', 'wb') as file:
        for chunk in model.iter_content(chunk_size=128):
            file.write(chunk)
    return index

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
    print(len(downloading))
    downloaded, errors = multi_process(download, downloading, process_number)
    downloaded = [x[1] for x in downloaded]
    failed = [x[1] for x in downloading if x[1] not in downloaded]
    for index in failed:
        if os.path.exists(save_dir + index + '.zip'):
            os.remove(save_dir + index + '.zip')
    if len(failed) > 0 or len(errors) > 0:
        print('please run again!')
    downloading = get_downloading()
    if len(downloading) > 0: 
        print('please run again!')
