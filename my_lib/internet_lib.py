# -*- coding: utf-8 -*-
"""Internet tools
"""
import os
import subprocess
import urllib.parse
import requests
from clint.textui import progress
import wget
from pathlib import Path
from typing import Union
import urllib3
from pathvalidate import sanitize_filepath, sanitize_filename

from .exception_lib import check_str_blank_throw_exception
from .check_type import is_blank_str
from .file_lib import re_create_new_filename

urllib3.disable_warnings()


def download_file(url_: str, file_save: Union[Path, str], b_overwrite=False, b_other_name=True, timeout=10, type_download=2) -> Path:
    """Download file from http

    Args:
        url_ (str): [description]
        file_save (str): [description]
        b_overwrite (bool, optional): Overwrite. Defaults to False.
        b_other_name (bool, optional): [description]. Defaults to True.
        timeout (int, optional): [description]. Defaults to 10.
        type_download (int, optional): [description]. Defaults to 1=Normal, 2=Normal with progress, 3=Curl, 4=Wget.
    Return:
        str: path of downloaded file
    """

    def download_file_by_wget(url_: str, file_save: str, b_overwrite=False, b_other_name=True):
        """Download file from http with wget

        Args:
            url (str):
            file_save (str):
        """
        check_str_blank_throw_exception(url_)
        check_str_blank_throw_exception(file_save)
        if os.path.exists(file_save) and not b_overwrite:
            if not b_other_name:
                return
            else:
                file_save = re_create_new_filename(file_save)

        wget.download(url_, file_save)

    def download_file_by_curl(url_: str, file_save: str, b_overwrite=False, b_other_name=True, b_chrome=True):
        """Download file from http

        Args:
            url (str):
            file_save (str):
        """
        """
        if "Linux" in platform.platform():
            curl_path="/usr/bin/curl"
        elif "Windows" in platform.platform():
            curl_path="C:\Windows\System32\curl.exe"
        else:
            curl_path="curl"
        """
        curl_path = "curl"
        check_str_blank_throw_exception(url_)
        check_str_blank_throw_exception(file_save)
        if os.path.exists(file_save) and not b_overwrite:
            if not b_other_name:
                return
            else:
                file_save = re_create_new_filename(file_save)

        cmd = f'{curl_path}###{url_}###-o###{file_save}'
        cmd = cmd.split("###")
        if b_chrome:
            cmd.extend(
                [
                    "--header",
                    "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36",
                ]
            )
        subprocess.call(cmd)

    if file_save and isinstance(file_save, Path):
        file_save = str(file_save)
    # file_save = sanitize_filepath(file_save)
    check_str_blank_throw_exception(url_)
    check_str_blank_throw_exception(file_save)
    if os.path.exists(file_save) and not b_overwrite:
        if not b_other_name:
            return file_save
        else:
            file_save = re_create_new_filename(file_save)

    if type_download == 3:
        download_file_by_curl(url_=url_, file_save=file_save, b_overwrite=b_overwrite, b_other_name=b_other_name)
    elif type_download == 4:
        download_file_by_wget(url_=url_, file_save=file_save, b_overwrite=b_overwrite, b_other_name=b_other_name)
    elif type_download == 1:
        req = requests.get(url_, stream=True, timeout=timeout, verify=False)
        with open(file_save, "wb") as f:
            for chunk in req.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    else:
        req = requests.get(url_, stream=True, timeout=timeout, verify=False)
        with open(file_save, "wb") as f:
            total_length = int(req.headers.get("content-length"))
            for ch in progress.bar(req.iter_content(chunk_size=2391975), expected_size=(total_length / 1024) + 1):
                if ch:
                    f.write(ch)
    return Path(file_save)


def download_file_to_folder(url_: str, folder: Union[Path, str], file_name=None, b_overwrite=False, b_other_name=True, type_download=2, timeout=10) -> Path:
    """Download file from http

    Args:
        url_ (str):
        folder (str):
        file_name (str, None):
        type_download (int, optional): [description]. Defaults to 1=Normal, 2=Normal with progress, 3=Curl, 4=Wget.
    Return:
        str: path of downloaded file
    """
    if folder and isinstance(folder, Path):
        folder = str(folder)
    check_str_blank_throw_exception(url_)
    check_str_blank_throw_exception(folder)
    file_save = ""
    if is_blank_str(file_name):
        file_name = get_file_name_from_url(url_)

    file_name = sanitize_filename(file_name)
    file_save = os.path.join(folder, file_name)

    if os.path.exists(file_save) and not b_overwrite:
        if not b_other_name:
            return Path(file_save)
        else:
            file_save = re_create_new_filename(file_save)
    file_save = download_file(url_=url_, file_save=file_save, b_overwrite=b_overwrite,
                              b_other_name=False, type_download=type_download, timeout=timeout)

    return file_save


def get_file_name_from_url(url: str, b_html=False):
    """Get filename from url

    Args:
        url (str): URL link

    Returns:
        str: filename
    """

    name = url.split("/")[-1]
    if "?" in name:
        name = name[: name.find("?")]
    if name and b_html and "." not in name:
        name += ".html"
    if "%" in name:
        name = urllib.parse.unquote(name)

    return name or "index.html"
