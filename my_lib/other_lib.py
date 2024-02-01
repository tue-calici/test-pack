import datetime as dt
from functools import wraps
import platform
from typing import List, Union
from datetime import datetime, date


def get_python_version() -> List[int]:
    return [int(x) for x in platform.python_version().split('.') if x]


def count_time_func(org_func):
    """
    Using
    @count_time_func
    def function_name(...)
    """
    def f_wrapper(*args, **kwargs):
        start_time = dt.datetime.now()
        ret_val = org_func(*args, **kwargs)
        end_time = dt.datetime.now()
        time_diff = end_time - start_time
        print(f"\n[{org_func.__name__}] function took {time_diff}")
        return ret_val
    return f_wrapper

def count_time_func_log(b_log=True):
    """Count time execute a function and write log file
    Using
    @count_time_func_log(True)
    def function_name(...)
    """

    def decorator_f(org_func):
        @wraps(org_func)
        def wrapper(*args, **kwargs):
            import logging
            start_time = dt.datetime.now()
            ret_val = org_func(*args, **kwargs)
            end_time = dt.datetime.now()
            time_diff = end_time - start_time
            if b_log:
                logging.info(f"\n[{org_func.__name__}] function took {time_diff}")
            return ret_val
        return wrapper
    return decorator_f

def datetime_to_str(input_: Union[date, datetime, None]=None, format_="%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime to string representation

    Args:
        input_ (date | datetime, optional): input value. Defaults to None.
        format_ (str, optional): Format style. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: format of datetime
            If input_ = None or invalid, return current time
    """
    if input_ is None:
        input_ = datetime.now().astimezone()

    return input_.strftime(format_)
