from pathlib import Path
from typing import Union
from bs4 import BeautifulSoup
import re
from .file_lib import load_file_to_str


def beautysoup_safe_load(file_path: Union[Path, str]) -> BeautifulSoup:
    return BeautifulSoup(load_file_to_str(file_path), "lxml")


def beautysoup_prettify(soup, b_tab=True, indent_length=2):
    """Convert BeautySoup to string with pretty

    Args:
        soup (bs4.element.Tag):
        b_tab (bool, optional): Defaults to True
        indent_length (int, optional): Defaults to 2. [description]
    """
    if not b_tab:
        if not indent_length:
            raise ValueError("indent_length parameter is not valid")
        _ = re.compile(r"^(\s*)", re.MULTILINE)
        return _.sub(r"\1" * indent_length, soup.prettify())

    return re.sub(r"^(\s*)", lambda m: len(m.group(0)) * "\t", soup.prettify(), flags=re.MULTILINE)

def beautysoup_get_element(soup, css_selector, b_multi=False, b_recursive=True):
    parent = soup
    ret = []
    for _ in css_selector:
        if parent is None:
            return [] if b_multi else None
        children = parent.select(_, recursive=b_recursive)
        if b_multi:
            ret = children
        else:
            ret = children[0] if children else None
        parent = children[0] if children else None
    return ret

def beautysoup_get_html_of_tag(soup=None):
    if soup is None:
        return ""
    ret = []
    for _ in soup.children:
        ret.append(str(_))
    return "".join(ret)
