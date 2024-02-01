# -*- coding: utf-8 -*-
"""Check type of data

"""


def is_string(s):
    """Check s is string or not

    Args:
        s  (str):

    Returns:
        bool
    """
    return isinstance(s, str)


def is_dict(d):
    """Check d is dict or not

    Args:
        d (dict)

    Returns:
        bool
    """
    return isinstance(d, dict)


def is_list(l):
    """Check l is list or not

    Args:
        l (list)

    Returns:
        bool
    """
    return isinstance(l, (list, set))


def is_blank_str(my_string):
    """Check string is empty or blank
    Args:
        my_string (str): Description

    Returns:
        bool: False if my_string empty or contains spaces only
    """
    return my_string is None or (isinstance(my_string, str) and not (my_string and my_string.strip()))


def is_cjk(character):
    """"
    Checks whether character is CJK.

        >>> is_cjk(u'\u33fe')
        True
        >>> is_cjk(u'\uFE5F')
        False

    :param character: The character that needs to be checked.
    :type character: char
    :return: bool
    """
    return any(start <= ord(character) <= end for start, end in [(4352, 4607), (11904, 42191), (43072, 43135), (44032, 55215), (63744, 64255), (65072, 65103), (65381, 65500), (131_072, 196_607), ])
