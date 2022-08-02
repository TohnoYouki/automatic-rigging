import multiprocessing
from queue import Empty
from multiprocessing import Pool
from inputimeout import inputimeout, TimeoutOccurred

def wrap_fun(params):
    number, fun, lock, input_queue, output_queue = params
    while True:
        try:
            index, data = input_queue.get(False)
            print(number, index)
            output = fun(data)
        except Exception as e:
            if isinstance(e, Empty): break
            else: continue
        else:
            lock.acquire()
            output_queue.put([index, output], False)
            lock.release()

def prepare(fun, data, number):
    manager = multiprocessing.Manager()
    lock = manager.Lock()
    input_queue = manager.Queue(len(data))
    output_queue = manager.Queue(len(data))
    for i in range(len(data)):
        input_queue.put([i, data[i]], False)
    params = [[i, fun, lock, input_queue, output_queue] for i in range(number)]
    pool = Pool(processes = number)
    result = pool.map_async(wrap_fun, params)
    return manager, lock, input_queue, output_queue, result, pool

def run_save(fun, lock, queue):
    lock.acquire()
    now_size = queue.qsize()
    temp_result = []
    for i in range(now_size):
        temp_result.append(queue.get(False))
    fun(temp_result)
    lock.release()

def multi_process(fun, data, number, save = None):
    prepare_result = prepare(fun, data, number)
    manager, lock, input_queue, output_queue, result, pool = prepare_result
    while not result.ready():
        try: c = inputimeout(timeout = 10)
        except TimeoutOccurred: c = None
        if save is not None: run_save(save, lock, output_queue)
        if c == 'quit()':
            lock.acquire()
            pool.terminate()
            lock.release()
            break
    if save is not None:
        run_save(save, lock, output_queue) 
        assert(output_queue.qsize() == 0)
        return None
    result = []
    while not output_queue.empty():
        result.append(output_queue.get(False))
    return result