import os, sys, json, zipfile
sys.path.append('../../../utils/')
from multiprocess import multi_process
sys.path.append('../../')
from input_output.convert import SceneConverter

zip_dir = './download models/'
save_dir = './extract/'

def get_pending():
    models = os.listdir(zip_dir)
    extracted = os.listdir(save_dir)
    extracted = set([x.split('_')[0] for x in extracted])
    models = [x for x in models if x.split('.')[0] not in extracted]
    return models

def parse(data, lock):
    status, results = [], []
    path = os.path.join(zip_dir, data)
    data = data.split('.')[0]
    try: file = zipfile.ZipFile(path, 'r')
    except: return [data, 'unzip failed']
    name_list = file.namelist()
    for name in name_list:
        extend = name.lower().split('.')
        if len(extend) <= 0 or extend[-1] not in ['dae', 'smd']: continue
        try: content = file.read(name)
        except:
            file.close()
            return [data, 'unzip failed']
        result = SceneConverter.convert(content, extend[-1])
        if result is not None and len(result) > 0:
            results.extend(result)
            status.append([name, 'parse successful'])
        elif result is None:
            status.append([name, 'parse failed'])
        else: status.append([name, 'zero failed'])
    file.close()
    if all([x[1] == 'parse successful' for x in status]):
        for i, scene in enumerate(results):
            name = data + '_' + str(i)
            scene.save(save_dir, name)
    return [data, status]

if __name__ == '__main__':
    process_number = 8
    models = get_pending()
    status, errors = multi_process(parse, models, process_number)
    status = [x[1] for x in status]
    if len(status) != len(models) or len(errors) > 0:
        print('please run again!')

    result = []
    for stat in status:
        if isinstance(stat[1], list):
            stat[1] = [x for x in stat[1] if x[1] != 'parse successful']
            if len(stat[1]) > 0: result.append(stat)
        else: result.append(stat)
    with open('parse_result.json', 'w') as file:
        file.write(json.dumps(result))