import os
import threading
from typing import List
from pathlib import Path

def split_array_advance(data: List[dict], item_name: str, part_num: int=2) -> List[dict]:
    """Split array based on value of item name

    Args:
        data (List[dict]): _description_
        item_name (str): _description_
        part_num (int, optional): _description_. Defaults to 2.

    Returns:
        List[dict]: _description_
    """
    if part_num<2:
        return data

    data = sorted(data, key=lambda x: x[item_name], reverse=True)
    ret = []
    arr_value = []

    for _ in range(part_num):
        ret.append([])
        arr_value.append(0)

    for val in data:
        # find array has min value
        i = arr_value.index(min(arr_value))
        ret[i].append(val)
        arr_value[i] += val[item_name]

    return ret

def split_array(arr:List, num:int=None, size:int=1, b_order = False):
    # sourcery skip: extract-method, remove-unnecessary-else
    """Split array by size

    Args:
        arr ([type]): [description]
        size (int, optional): Defaults to 1. Number of children arr.
        num ([int], optional): Defaults to None. Size of children.
        b_order ([bool], optional): Defaults to False. []
    Raises:
        AssertionError: [description]

    Returns:
        [type]: [description]
    """
    if not arr:
        return []
    length = len(arr)
    if num:
        if num < 1:
            raise AssertionError("Num is < 1")
        num = min(num, length)
        if not b_order:
            size, mod = divmod(length, num)
            size_1 = size + 1
            ret = [arr[i:i + size_1] for i in range(0, mod*size_1, size_1)]
            arr = arr[mod * size_1:]
            length = len(arr)
            ret.extend([arr[i:i + size] for i in range(0, length, size)])
        else:
            ret = [[] for _ in range(num)]
            for i, v in enumerate(arr):
                ret[i % num].append(v)
        return ret
    else:
        if size < 1:
            raise AssertionError("Size is < 1")

        return [arr[i:i + size] for i in range(0, length, size)]


class OtherLocalThread(threading.Thread):
    """Thread job"""

    def __init__(self, *args, items=None, func=None, lock=None, output_arr=None, output_index=-1):
        """Init

        Args:
            file_list (list[dict]): Description
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.items = items
        self.lock = lock
        self.output_arr = output_arr
        self.output_index = output_index

    def run(self):
        """Running"""
        if self.func and self.items:
            for _ in self.items:
                try:
                    kwarg = {'item': _}
                    if self.lock:
                        kwarg['lock'] = self.lock
                    if self.output_arr:
                        kwarg['output_arr'] = self.output_arr
                        kwarg['output_index'] = self.output_index

                    self.func(*self.args, **kwarg)
                except Exception as ex:
                    raise ex

def thread_execute(*args, thread_num=5, func=None, list_arr=None, b_lock=False, b_split_arr=True, output_arr=None):
    """Execute by threads

    Args:
        thread_num (int, optional): Number of threads. Defaults to 5.
        func ([function], optional): Function execute. Function must has arg item, item is item in list_arr
        list_arr (list): list_arr
        b_lock ([bool], optional): Default to False, using threading.Lock()
        b_split_arr ([bool], optional): Default to True, split list_arr or not
        output_arr ([list], optional): Default to None, store output result of function
    """

    if thread_num < 1:
        raise AssertionError("thread_num is < 1")
    if not func:
        raise AssertionError("func parameter is None.")
    if not list_arr:
        raise AssertionError("list_arr parameter is None or empty.")

    lock = threading.Lock() if b_lock else None
    list_arr_splited = split_array(list_arr, num=thread_num) if b_split_arr else list_arr

    list_thread = []
    for n, _ in enumerate(list_arr_splited):
        if output_arr and len(output_arr) == len(list_arr_splited):
            thread = OtherLocalThread(*args, items=_, func=func, lock=lock, output_arr=output_arr, output_index=n)
        else:
            thread = OtherLocalThread(*args, items=_, func=func, lock=lock)
        thread.start()
        list_thread.append(thread)

    # Wait until all threads have finished
    for _ in list_thread:
        _.join()


def multi_process_execute(*args, process_num=5, func=None, list_arr=None, b_split_arr=True, output_file: Path = None, b_delete_part_file=True):
    from multiprocessing import Process, Value, Lock
    from .file_lib import write_dict_to_json_file_simple, load_json_file
    """Execute by multi process

    Args:
        process_num (int, optional): Number of processes. Defaults to 5.
        func ([function], optional): Function execute. Function must has arg item, item is item in list_arr
        list_arr (list): list_arr
        b_split_arr ([bool], optional): Default to True, split list_arr or not
        output_arr ([Path], optional): Default to None, file stores output data
        b_delete_part_file ([bool], optional): Default to True, will delete part file *.xxx file
    """

    class Counter(object):
        def __init__(self, initval=0):
            self.val = Value('i', initval)
            self.lock = Lock()

        def increment(self):
            with self.lock:
                self.val.value += 1

        def value(self):
            with self.lock:
                return self.val.value

    def process_of_thread(*args, func=None, items=None, output_file: Path = None, counter=None, process_no=-1):
        if not items or not func:
            return

        data = []
        for item in items:
            params = {'item': item}
            if 'counter' in func.__code__.co_varnames:
                params['counter'] = counter
            if 'process_no' in func.__code__.co_varnames:
                params['process_no'] = process_no
            ret = func(*args, **params)
            if output_file:
                data.append(ret)
        if output_file:
            write_dict_to_json_file_simple(output_file, data)

    if process_num < 1:
        raise AssertionError("process_num is < 1")
    if not func:
        raise AssertionError("func parameter is None.")
    if not list_arr:
        raise AssertionError("items parameter is None or empty.")

    list_arr_splited = split_array(list_arr, num=process_num) if b_split_arr else list_arr
    list_processes = []
    if output_file:
        # Create folder of output_file
        output_file.parent.mkdir(parents=True, exist_ok=True)
    counter = Counter(0)
    for n, v in enumerate(list_arr_splited):
        kwargs = {
            'items': v,
            'func': func,
            'counter': counter,
            'process_no': n,
        }
        if output_file:
            kwargs['output_file'] = output_file.with_suffix(f"{output_file.suffix}.{n:03d}")

        p = Process(args=args, kwargs=kwargs, target=process_of_thread)
        list_processes.append(p)
        p.start()

    # completing process
    for p in list_processes:
        p.join()

    if output_file:
        data = []
        for n, v in enumerate(list_arr_splited):
            n_file = output_file.with_suffix(f"{output_file.suffix}.{n:03d}")
            data.extend(load_json_file(n_file))
            if b_delete_part_file:
                os.remove(n_file)
        write_dict_to_json_file_simple(output_file, data)