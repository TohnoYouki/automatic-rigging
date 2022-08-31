import multiprocessing
from queue import Empty
from multiprocessing import Pool
from inputimeout import inputimeout, TimeoutOccurred

def wrap_fun(params):
    number, fun, lock, input_queue, output_queue, error_queue = params
    while True:
        try:
            index, data = input_queue.get(False)
            print(number, index)
            output = fun(data, lock)
        except Exception as e:
            if isinstance(e, Empty): break
            else:
                print('process', number, 'has error:', e) 
                lock.acquire()
                error_queue.put([index, data], False)
                lock.release()
                continue
        else:
            lock.acquire()
            output_queue.put([index, output], False)
            lock.release()

def prepare(fun, data, number):
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    input_queue = manager.Queue(len(data))
    output_queue = manager.Queue(len(data))
    error_queue = manager.Queue(len(data))
    for i in range(len(data)):
        input_queue.put([i, data[i]], False)
    params = [[i, fun, lock, input_queue, output_queue, error_queue] 
               for i in range(number)]
    pool = Pool(processes = number)
    result = pool.map_async(wrap_fun, params)
    return manager, lock, input_queue, output_queue, error_queue, result, pool

def multi_process(fun, data, number):
    prepare_result = prepare(fun, data, number)
    manager, lock, input_queue, output_queue, \
        error_queue, result, pool = prepare_result
    while not result.ready():
        try: c = inputimeout(timeout = 10)
        except TimeoutOccurred: c = None
        if c == 'quit()':
            lock.acquire()
            pool.terminate()
            lock.release()
            break
    result, error = [], []
    while not output_queue.empty():
        result.append(output_queue.get(False))
    while not error_queue.empty():
        error.append(error_queue.get(False))
    return result, error