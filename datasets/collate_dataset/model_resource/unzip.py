import os
import shutil
import zipfile
from multiprocess import multi_process

formats = ['dae', 'smd']
all_zip_dir = './zip/'
all_unzip_dir = './unzip/'
unzip_failed_dir = './unzip failed/'

def copy_format_file(src_dir, dest_dir, formats):
    for sub_dir in os.listdir(src_dir):
        sub_path = os.path.join(src_dir, sub_dir)
        if os.path.isdir(sub_path):
            copy_format_file(sub_path, dest_dir, formats)
        elif os.path.isfile(sub_path):
            file_format = sub_dir.split('.')[-1].lower()
            if file_format not in formats: continue
            shutil.copy(sub_path, os.path.join(dest_dir, sub_dir))

def unzip(zip_path, unzip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as file:
            file.extractall(unzip_path)
    except: 
        print('unzip ', zip_path, ' error')
        return False
    return True

def extract(model):
    zip_file = all_zip_dir + model + '.zip'
    temp_dir = all_unzip_dir + 't' + model
    unzip_dir = all_unzip_dir + model
    if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
    if not unzip(zip_file, temp_dir): 
        if os.path.exists(temp_dir): shutil.rmtree(temp_dir)
        return model
    if os.path.exists(unzip_dir): shutil.rmtree(unzip_dir)
    os.mkdir(unzip_dir)
    copy_format_file(temp_dir, unzip_dir, formats)
    shutil.rmtree(temp_dir)
    return None

def get_unzip_models():
    models = [x.split('.')[0] for x in os.listdir(all_zip_dir)]
    unziped = [x for x in os.listdir(all_unzip_dir)]
    models = [x for x in models if x not in unziped]
    return models

if __name__ == '__main__':
    process_number = 8
    models = get_unzip_models()
    failed = multi_process(extract, models, process_number)
    failed = [x[1] for x in failed if x[1] is not None]
    for number in failed:
        shutil.copy(all_zip_dir + number + '.zip', unzip_failed_dir + number + '.zip')
    
    models = get_unzip_models()
    if len(models) != len(failed) or any([x not in models for x in failed]):
        print('please run again!')