# -*- coding: utf-8 -*-
"""File tool function
"""
from __future__ import print_function  # Compatible python 2 and 3
from types import GeneratorType
from enum import Enum

import json
import os
import shutil
import zipfile
import logging
import datetime as dt
from .check_type import is_list, is_blank_str
from .other_lib import get_python_version
from pathlib import Path
from typing import Union, List
import fnmatch


def __convert_path(file_path: Union[Path, str], b_check_exists: bool = False, b_create_parent: bool = False) -> Path:
    # Convert str to Path
    if isinstance(file_path, str):
        file_path = file_path.strip()

    if not file_path:
        raise ValueError("file_path is not None or empty")

    file_path = Path(file_path)

    # Check exists
    if b_check_exists and not file_path.exists():
        raise FileNotFoundError(f"Path {file_path} does not exist")

    # Create parent folder
    if b_create_parent:
        file_path.parent.mkdir(exist_ok=True, parents=True)

    return file_path


def call_test__convert_path(file_path: Union[Path, str], b_check_exists=False):
    return __convert_path(file_path, b_check_exists=b_check_exists)


def __glob_folder(folder: Path, pattern: str, is_folder=False, is_file=False, exclude_names: List[str] = None, is_exclude_names_case=True):
    """_summary_

    Args:
        folder (str):
        pattern (str, optional): Defaults to '*'.
        is_folder (bool, optional): return folders in result. Defaults to False.
        is_file (bool, optional): return files in result. Defaults to False.
        exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
        is_exclude_names_case (bool, optional): Case sensitive on match exclude names. Defaults to True.

    Returns:
        _type_: _description_
    """
    ret = []
    if exclude_names is None:
        exclude_names = []
    compare_func = fnmatch.fnmatchcase if is_exclude_names_case else fnmatch.fnmatch
    for item in folder.glob(pattern):
        b_match = False
        for ex_name in exclude_names:
            relative_path = item.relative_to(folder)
            if compare_func(str(relative_path), ex_name):
                b_match = True
                break
        if not b_match:
            if is_folder and item.is_dir():
                ret.append(item)
            if is_file and item.is_file():
                ret.append(item)
    return ret


def list_sub_folders(folder: Union[Path, str], pattern: str = '*', level=0, b_print=False, b_log=False, b_only_leaf_folder=False, exclude_names: List[str] = None, is_exclude_names_case=True) -> List[Path]:
    """List child folders of parent folder

    Args:
        folder (str):
        pattern (str, optional): Defaults to '*'.
        level:
            -1: no limit
            0: current folder
        b_print (bool, optional): Show folder path on screen. Defaults to False.
        b_log (bool, optional): Show folder path on logging. Defaults to False.
        b_only_leaf_folder (bool, optional): Only show folders have in level=0. Defaults to False.
        exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
        is_exclude_names_case (bool, optional): Case sensitive on match exclude names. Defaults to True.

    Returns:
        List[Path]: list of folders' path
    """
    if b_print:
        print(folder)
    if b_log:
        logging.info(str(folder))

    if level < 0:
        level = -1
    if '/' in pattern:
        raise ValueError('Pattern must not include /')
    if not folder:
        raise ValueError("folder is not empty or None")
    folder = __convert_path(folder, b_check_exists=True)
    ret = []
    if level == -1:
        return __glob_folder(folder, pattern=f'**/{pattern}', is_folder=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)

    if b_only_leaf_folder and level == 0:
        return __glob_folder(folder, pattern=pattern, is_folder=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)
    elif not b_only_leaf_folder:
        ret = __glob_folder(folder, pattern=pattern, is_folder=True,
                            exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)

    if (level > 0):
        folders = __glob_folder(folder, pattern='*', is_folder=True,
                                exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)
        for _ in folders:
            ret.extend(list_sub_folders(_, pattern=pattern, level=level - 1, b_print=b_print, b_log=b_log,
                                        b_only_leaf_folder=b_only_leaf_folder, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case))

    return ret


def list_sub_folders_str(folder: Union[Path, str], pattern: str = '*', level=0, b_print=False, b_log=False, b_only_leaf_folder=False, exclude_names: List[str] = None, is_exclude_names_case=True) -> List[str]:
    """List child folders of parent folder

    Args:
        folder (Path | str)
        pattern (str, optional): Defaults to '*'.
        level:
            -1: no limit
            0: current folder
        b_print (bool, optional): _description_. Defaults to False.
        b_log (bool, optional): _description_. Defaults to False.
        b_only_leaf_folder (bool, optional): Only show folders have in level=0. Defaults to False.
        exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
        is_exclude_names_case (bool, optional): Case sensitive on match exclude names. Defaults to True.

    Returns:
        List[str]: _description_
    """
    ret = list_sub_folders(folder, pattern, level, b_print=b_print, b_log=b_log,
            b_only_leaf_folder=b_only_leaf_folder, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)
    ret = [str(f) for f in ret]
    return ret


def list_files(folder: Union[Path, str], pattern: str = '*', level=0, b_print=False, b_log=False, b_only_leaf_folder=False, exclude_names: List[str] = None, is_exclude_names_case=True) -> List[Path]:
    """List child files of parent folder

    Args:
        folder (Path | str)
        pattern (str, optional): Defaults to '*'.
        level:
            -1: no limit
            0: current folder
        b_print (bool, optional): Show folder path on screen. Defaults to False.
        b_log (bool, optional): Show folder path on logging. Defaults to False.
        b_only_leaf_folder (bool, optional): Only show files have in level=0. Defaults to False.
        exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
        is_exclude_names_case (bool, optional): Case sensitive on match exclude names. Defaults to True.

    Returns:
        List[Path]: list of files' path
    """

    if '/' in pattern:
        raise ValueError('Pattern must not include /')
    if not folder:
        raise ValueError("folder is not empty or None")
    if b_print:
        print(folder)
    if b_log:
        logging.info(str(folder))

    if level < 0:
        level = -1
    folder = __convert_path(folder, b_check_exists=True)
    ret = []
    if level == -1:
        return __glob_folder(folder, pattern=f'**/{pattern}', is_file=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)

    if b_only_leaf_folder and level == 0:
        return __glob_folder(folder, pattern=pattern, is_file=True, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)
    elif not b_only_leaf_folder:
        ret = __glob_folder(folder, pattern=pattern, is_file=True, exclude_names=exclude_names,
                            is_exclude_names_case=is_exclude_names_case)

    if (level > 0):
        folders = __glob_folder(folder, pattern='*', is_folder=True, exclude_names=exclude_names,
                                is_exclude_names_case=is_exclude_names_case)
        for _ in folders:
            ret.extend(list_files(_, pattern=pattern, level=level - 1, b_print=b_print,
                                b_log=b_log, b_only_leaf_folder=b_only_leaf_folder, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case))

    return ret


def list_files_str(folder: Union[Path, str], pattern: str = '*', level=0, b_print=False, b_log=False, b_only_leaf_folder=False, exclude_names: List[str] = None, is_exclude_names_case=True) -> List[str]:
    """List child files of parent folder

    Args:
        folder (Union[Path, str]): _description_
        pattern (str, optional): _description_. Defaults to '*'.
        level (int, optional): _description_. Defaults to 0.
        b_print (bool, optional): _description_. Defaults to False.
        b_log (bool, optional): _description_. Defaults to False.
        b_only_leaf_folder (bool, optional): Only show files have in level=0. Defaults to False.
        exclude_names (List[str], optional): ['*a.html', '???']. Defaults to None.
        is_exclude_names_case (bool, optional): Case sensitive on match exclude names. Defaults to True.

    Returns:
        List[str]: _description_
    """
    ret = list_files(folder, pattern=pattern, level=level, b_print=b_print,
                    b_log=b_log, b_only_leaf_folder=b_only_leaf_folder, exclude_names=exclude_names, is_exclude_names_case=is_exclude_names_case)
    ret = [str(f) for f in ret]
    return ret


def load_file_to_str(file_path: Union[Path, str], encoding="utf-8", errors="ignore", b_rstrip=True) -> str:
    """_summary_

    Args:
        file_path (Path | str)
        encoding (str, optional): Defaults to "utf-8".
        errors (str, optional): Defaults to "ignore".
        b_rstrip (bool, optional): Defaults to "True". Right strip space, \r, \n
    Returns:
        str: data of file
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        s = f_source.read()
    if b_rstrip:
        s = s.rstrip(" \r\n")
    return s


def load_file_to_list_str_n_head(file_path: Union[Path, str], b_remove_blank_str=False, encoding="utf-8", errors="ignore", row_num=10) -> List[str]:
    """Load text unicode file to list(string)

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
    Returns:
        List[str]: list of string containt file's content
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    lines = []
    n = 0
    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        while n < row_num:
            line = f_source.readline()
            if len(line) == 0:
                break
            line = line.rstrip("\r\n")
            if not b_remove_blank_str or not is_blank_str(line):
                n += 1
                lines.append(line)

    return lines


def load_file_to_list_str(file_path: Union[Path, str], b_remove_blank_str=False, encoding="utf-8", errors="ignore") -> List[str]:
    """Load text unicode file to list(string)

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
    Returns:
        List[str]: list of string containt file's content
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    with open(file_path, "r", encoding=encoding, errors=errors) as f_source:
        lines = f_source.readlines()

    lines = [x.rstrip("\r\n") for x in lines if (
        b_remove_blank_str and not is_blank_str(x)) or not b_remove_blank_str]

    return lines


def write_str_to_file(file_path: Union[Path, str], data: str, encoding="utf-8", newline="\n"):
    """Write string data to text unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    if is_blank_str(data):
        raise ValueError("data is not empty")

    with open(file_path, "w+", encoding=encoding, newline=newline) as f_dest:
        f_dest.write(data)


def write_list_str_to_file(file_path: Union[Path, str], data: List[str], b_remove_blank_str=False, newline="\n", encoding="utf-8"):
    """Write list of string to unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    if not is_list(data):
        raise ValueError("data must be list(str)")

    new_data = []
    for item in data:
        if b_remove_blank_str and is_blank_str(item):
            continue
        if item.endswith(newline):
            new_data.append(item)
        else:
            new_data.append(item + newline)

    # remove last blank line
    if new_data:
        new_data[-1] = new_data[-1].rstrip("\r\n")

    with open(file_path, "w+", newline=newline, encoding=encoding) as f_dest:
        f_dest.writelines(new_data)


def append_str_to_file(file_path: Union[Path, str], data, encoding="utf-8", lock=None):
    """Append string data to end of unicode file

    Args:
        file_path (str): path of source file
        data (str): data
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        lock: using when running thread
    """

    file_path = __convert_path(file_path, b_create_parent=True)
    if is_blank_str(data):
        raise ValueError("data is not empty")

    if lock:
        # acquire the lock
        lock.acquire()

    with open(file_path, "a", encoding=encoding) as f_dest:
        f_dest.write(data)

    if lock:
        # acquire the lock
        lock.release()


def append_list_str_to_file(file_path: Union[Path, str], data: List[str], b_remove_blank_str=False, newline="\n", encoding="utf-8", lock=None):
    """Append string data to end of unicode file

    Args:
        encoding (str): default utf-8 (utf-8-sig: UTF8 with bom)
        newline (str): None, '', '\\n', '\\r', and '\\r\\n'
        lock: using when running thread
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    if not is_list(data):
        raise ValueError("data must be list(str)")

    n = len(data)
    if lock:
        # acquire the lock
        lock.acquire()

    with open(file_path, "a", encoding=encoding, newline=newline) as f_dest:
        for i, item in enumerate(data):
            if b_remove_blank_str and is_blank_str(item):
                continue

            if i < n - 1:
                item = item.rstrip("\r\n") + newline

            # Remove \r \n in last line
            if i == n - 1:
                item = item.rstrip(newline)

            f_dest.write(item)
    if lock:
        # acquire the lock
        lock.release()


def create_zip(src: Union[Path, str], dst: Union[Path, str] = None):
    """Create a zip file

    Args:
        src : source folder
        dst : dest file

    """
    src = __convert_path(src)
    dst = __convert_path(dst, b_create_parent=True) if dst else src

    if dst.suffix != 'zip':
        dst = dst.with_suffix(".zip")

    zf = zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for dirname, _, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            zf.write(absname, arcname)
    zf.close()


def extract_zip(src: Union[Path, str], dst: Union[Path, str] = None):
    """Create a zip file

    Args:
        src : source folder
        dst : dest file
    """

    if not src:
        raise ValueError("src is not empty")
    src = __convert_path(src, b_check_exists=True)
    if not dst:
        dst = src.parent / src.stem
    dst = __convert_path(dst)
    dst.mkdir(exist_ok=True, parents=True)

    with zipfile.ZipFile(src, "r") as zip_ref:
        zip_ref.extractall(dst)


def create_folder(dest_folder: Union[Path, str], force_delete=False):
    """Create new folder

    Args:
        dest_folder (str): dest folder
        force_delete (bool, optional): True: delete exists folder
    """
    if not dest_folder:
        raise ValueError("Destination folder is not empty")
    if isinstance(dest_folder, Path):
        dest_folder = str(dest_folder)

    if os.path.isdir(dest_folder) and force_delete:
        shutil.rmtree(dest_folder, True)
    elif os.path.isfile(dest_folder):
        raise ValueError(f"File {dest_folder} existed")

    if not os.path.isdir(dest_folder) and not os.path.islink(dest_folder):
        dest_folder = Path(dest_folder)
        dest_folder.mkdir(exist_ok=True, parents=True)


def load_json_file(
    file_path: Union[Path, str], parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, encoding="utf-8"
):
    """Load json data from file

    Returns:
        dict: json data

    """
    file_path = __convert_path(file_path, b_check_exists=True)
    python_v = get_python_version()
    with open(file_path, "r", encoding=encoding) as f_source:
        if python_v[0]>=3 and python_v[1]>=9:
            json_data = json.load(
                f_source,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                object_pairs_hook=object_pairs_hook,
                # encoding="utf-8",    from python 3.9 not need
            )
        else:
            json_data = json.load(
                f_source,
                parse_float=parse_float,
                parse_int=parse_int,
                parse_constant=parse_constant,
                object_pairs_hook=object_pairs_hook,
                encoding=encoding,
            )
    return json_data


class UniversalEncoder(json.JSONEncoder):
    ENCODER_BY_TYPE = {
        dt.datetime: lambda o: o.isoformat(),
        dt.date: lambda o: o.isoformat(),
        dt.time: lambda o: o.isoformat(),
        set: list,
        frozenset: list,
        GeneratorType: list,
        bytes: lambda o: o.decode(),
    }

    def default(self, o):
        if isinstance(o, Enum):
            return o.value
        for k, v in self.ENCODER_BY_TYPE.items():
            if isinstance(o, k):
                encoder = v
                return encoder(o)

        if type(o) == "pydantic.main.BaseModel":
            return o.dict()

        try:
            return super().default(o)
        except TypeError:
            try:
                return o.__dict__
            except AttributeError:
                return str(o)


def write_dict_to_json_file(file_path: Union[Path, str], data, encoding="utf-8", newline="\n", indent=2):
    """Write dict data to text file with json format

    Args:
        file_path (str): dest file path
        data (dict): dictionary data
        encoding (str):
    """
    file_path = __convert_path(file_path, b_create_parent=True)

    with open(file_path, "w+", encoding=encoding, newline=newline) as f_dest:
        # Save direct to text file
        json.dump(data, f_dest, ensure_ascii=False, indent=indent, cls=UniversalEncoder)


def write_dict_to_json_file_simple(file_path: Union[Path, str], data, encoding="utf-8", indent=0):
    """Write dict data to text file with no format

    Args:
        file_path (str): dest file path
        data (dict): dictionary data
        encoding (str):
    """
    file_path = __convert_path(file_path, b_create_parent=True)

    with open(file_path, "w+", encoding=encoding) as f_dest:
        # Save direct to text file
        if indent < 0:
            json.dump(data, f_dest, ensure_ascii=False)
        else:
            json.dump(data, f_dest, ensure_ascii=False, indent=indent)


def get_current_dir(path: Union[Path, str]) -> Path:
    """Get current dir of path

    Args:
        path (str): source path

    Returns:
        str
    """
    return __convert_path(path).parent.resolve()


def find_empty_folder(folder: Union[Path, str], b_add_self=False) -> List[str]:
    """Find empty folder

    Args:
        folder (str): folder
        b_add_self (bool, optional): Default to False,  if True current folder will be add to return list if it is empty

    Return:
        list: list of empty folder
    """
    files = list_files(folder=folder, level=0)
    folders = list_sub_folders(folder=folder, level=0)
    ret = []
    if not files and not folders and b_add_self:
        ret = [str(folder)]

    for _ in folders:
        ret.extend(find_empty_folder(_, b_add_self=True))

    return ret


def remove_empty_folder(folder: Union[Path, str], b_add_self=False):
    """Remove empty folder

    Args:
        folder (Union[Path, str]): _description_
        b_add_self (bool, optional): Default to False, if True current folder will be remove if it is empty
    """
    list_dir = find_empty_folder(folder, b_add_self)
    while list_dir:
        for _ in list_dir:
            os.rmdir(_)
        list_dir = find_empty_folder(folder, b_add_self)


def start_logging(file_path: Union[Path, str], renew=False, level=logging.INFO, b_terminal=True):
    """Start loging process, create file log based on py file_path or file_path if file_path isn't python file

    Args:
        renew (bool, optional):
            True: delete current log file and create new log file
    """
    file_path = __convert_path(file_path, b_create_parent=True)
    file_name = file_path.name
    if file_path.suffix == ".py":
        file_path = file_path.with_suffix(".log")

    if file_path.is_dir():
        raise ValueError(f"{str(file_path)} is directory")
    if renew and file_path.exists():
        os.remove(file_path)
    formatter = "%(asctime)s %(levelname)s: %(name)s->%(funcName)s - %(message)s"
    handlers = [logging.FileHandler(file_path, "w+" if renew else "a+", "utf-8")]
    if b_terminal:
        from colorama import Fore, Back, Style
        colors = {
            "DEBUG": Fore.BLUE,
            "INFO": Fore.CYAN,
            "WARNING": Fore.YELLOW + Style.BRIGHT,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.MAGENTA + Style.BRIGHT
        }

        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                msg = logging.Formatter.format(self, record)
                if record.levelname in colors:
                    msg = colors[record.levelname] + msg + Fore.RESET
                return msg
        s_handler = logging.StreamHandler()
        s_handler.setFormatter(ColoredFormatter(formatter))
        handlers.append(s_handler)

    logging.basicConfig(
        level=level,  # minimum level capture in the file
        format=formatter,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logging.info(
        f"--------------------------------------------- {file_name} - {dt.datetime.now()} ---------------------------------------------------"
    )


def process_files_in_folder(*args, folder: Union[Path, str] = None, func=None, pattern: str = '*', level=0):
    """

    Args:
        func : Must be func_name(file_path, *args)
    """
    folder = __convert_path(folder, b_check_exists=True)
    if not func:
        raise ValueError("Invalid parameter 'func'")

    files = list_files(folder, pattern, level)

    for _ in files:
        func(_, *args)


def is_binary_file(file_path: Union[Path, str]):
    """Return true if the given filename is binary.

    Raises an EnvironmentError if the file does not exist or cannot be
    accessed.
    """
    file_path = __convert_path(file_path, b_check_exists=True)

    fin = open(file_path, "rb")
    ret = False
    try:
        CHUNK_SIZE = 1024
        while 1:
            chunk = fin.read(CHUNK_SIZE)
            if 0 in chunk:  # found null byte
                ret = True
                break
            if len(chunk) < CHUNK_SIZE:
                break  # done
    finally:
        fin.close()

    return ret


def move_items_in_folder(source_folder: Union[Path, str], dest_folder: Union[Path, str]):
    """Move all items in 1 folder to other folder

    Args:
        source_folder (str): [description]
        dest_folder (str): [description]
    """
    if isinstance(source_folder, Path):
        source_folder = str(source_folder)
    if isinstance(source_folder, Path):
        dest_folder = str(dest_folder)
    if not source_folder or not os.path.isdir(source_folder):
        raise ValueError(f"Source folder {source_folder} is not correct")
    if is_blank_str(dest_folder):
        raise ValueError(f"Dest folder {dest_folder} is not correct")

    create_folder(dest_folder)
    files = os.listdir(source_folder)

    for _ in files:
        shutil.move(os.path.join(source_folder, _), os.path.join(dest_folder, _))


def re_create_new_filename(file_path: Union[Path, str], sep='-') -> Path:
    """Recreate new file name if it exists

    Args:
        file_path (str | Path): [description]

    Returns:
        str: generate new file name if file_name exists
    """
    file_path = __convert_path(file_path)

    if not file_path.exists():
        return file_path

    name = file_path.stem
    n = 1
    new_file_path = file_path.with_name(f"{name}{sep}{n}").with_suffix(file_path.suffix)
    while new_file_path.exists():
        n += 1
        new_file_path = file_path.with_name(f"{name}{sep}{n}").with_suffix(file_path.suffix)

    return new_file_path


def count_files(folder: Union[Path, str], file_type=None) -> int:
    """
    count files in one folders
    """
    folder = __convert_path(folder, b_check_exists=True)
    gen_file = folder.iterdir()
    b_end = False
    count = 0
    while not b_end:
        try:
            file = next(gen_file)
            if not file.is_file():
                continue
            if file_type is None or (file_type is not None and file.name.endswith(file_type)):
                count += 1
        except StopIteration:
            b_end = True
    return count


def copy_folder(src: Union[Path, str], dest: Union[Path, str], b_overwrite: bool = True, ignore_types: List[str] = None, include_types: List[str] = None, ignore_folder: List[str] = None, b_recursive=True):
    """Copy src/* to dest/*

    Args:
        src (_type_): _description_
        dest (_type_): _description_
        b_overwrite (bool, optional): Overwrite?. Defaults to True.
        ignore_types (list, optional): Ignore types. Example: ['chm','html']. Defaults to None.
        include_types (list, optional): Include types. Example: ['chm','html']. Defaults to None.
        ignore_folder (list, optional): Ignore folders. Example: folder1. Defaults to None.
        b_recursive (bool, optional): Copy subfolder's contents.. Defaults to True.

    Raises:
        RuntimeError: _description_
    """
    src = __convert_path(src, True)
    dest = __convert_path(dest)

    if src.is_file() or src.is_symlink():
        return
    if dest.exists() and dest.is_file():
        raise ValueError(f"{str(dest)} is a file")
    dest.mkdir(parents=True, exist_ok=True)
    for f in src.glob('*'):
        if f.is_dir():
            if ignore_folder and f.name in ignore_folder:
                continue
            if b_recursive:
                copy_folder(f, dest / f.name, b_overwrite=b_overwrite, ignore_types=ignore_types, include_types=include_types, ignore_folder=ignore_folder, b_recursive=b_recursive
                            )
            else:
                (dest / f.name).mkdir(parents=True, exist_ok=True)
        else:
            file_type = f.suffix.lstrip('.')
            if ignore_types and file_type in ignore_types:
                continue
            if not b_overwrite and (dest / f.name).exists():
                continue
            if (include_types and file_type in include_types) or not include_types:
                shutil.copy(f, dest)
