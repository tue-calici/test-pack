# -*- coding: utf-8 -*-
"""Contains expection class
"""
from __future__ import print_function  # Compatible python 2 and 3

from http import HTTPStatus
from .check_type import is_string, is_list, is_blank_str

INVALID_PARAMETER = "Invalid parameter"
ERROR_IN_COMPUTING = "Error in computing"


class FatalError(Exception):
    """Default exception

    Attributes:
        message (str): message of exception
    """

    message = None

    def __init__(self, message):
        """
        Args:
            message (str):
        """
        self.message = message
        super().__init__(message)

    def __repr__(self):
        """Convert to string

        Returns:
            str:
        """
        return self.message


class FlaskFatalError(Exception):
    """Exception for flask

    Attributes:
        message (str): Description
        payload (TYPE): Description
        status_code (HTTPStatus): Description
    """

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message=None, status_code=None, payload=None):
        """Constructor class

        Args:
            message (str, optional): message of exception
            status_code (HTTPStatus, optional): HTTP status code
            payload (str, optional):
        """
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        if not self.message:
            self.message = ERROR_IN_COMPUTING
        if not self.status_code:
            self.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        self.payload = payload

    def to_dict(self):
        """Convert this exception to dict form

        Returns:
            str: dict to
        """
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def check_str_blank_throw_exception(s, param_name=None):
    """Check str, if is None or empty then raise FatalException

    Args:
        s (str | list): [description]
        param_name ([str], optional): Defaults to None.
    """
    if not is_string(s) and not is_list(s):
        if is_blank_str(param_name):
            raise ValueError("This parameter is not string or list.")
        else:
            raise ValueError(f"{param_name} is not string or list.")
    if is_string(s) and is_blank_str(s):
        if is_blank_str(param_name):
            raise ValueError("This parameter is blank string.")
        else:
            raise ValueError(f"{param_name} is blank string.")
    if is_list(s):
        param_l = []
        msg = []
        if param_name and is_string(param_name):
            param_l = list(map(lambda x: x.strip(), param_name.split(",")))
        for n, _ in enumerate(s):
            if not is_string(_):
                if len(param_l) > n:
                    msg.append(f"{param_l[n]} is not string or list")
                else:
                    msg.append("One parameter in list is not string")
            elif is_blank_str(_):
                if len(param_l) > n:
                    msg.append(f"{param_l[n]} parameter is blank")
                else:
                    msg.append("One parameter is blank")
        if msg:
            msg = ", ".join(msg)
            raise ValueError(msg)


def check_object_none_throw_exception(obj, param_name=None):
    """Check str, if is None or empty then raise FatalException

    Args:
        obj
        param_name ([str], optional): Defaults to None. [description]
    """
    if obj is None:
        if is_blank_str(param_name):
            raise ValueError("This parameter is None.")
        else:
            raise ValueError(f"{param_name} is None.")
    if is_list(obj):
        msg = []
        param_l = param_name.split(",") if param_name and is_string(param_name) else []
        for n, _ in enumerate(obj):
            if _ is None:
                if len(param_l) > n:
                    msg.append(f"{param_l[n]} parameter is None.")
                else:
                    msg.append("One parameter is None.")

        if msg:
            raise ValueError(", ".join(msg))
