# encoding: utf-8
""" Some useful functions for interacting with the current request.
"""

from ckan.common import request


def get_cookie(field_name, default=None):
    """ Get the value of a cookie, or the default value if not present.
    """
    return request.cookies.get(field_name, default)


def get_query_params():
    return getattr(request, 'GET', None) or getattr(request, 'args', {})


def get_post_params():
    return getattr(request, 'POST', None) or getattr(request, 'form', {})


def get_first_post_param(field_name, default=None):
    """ Retrieve the first POST parameter with the specified name
    for the current request.

    This uses 'request.POST' for Pylons and 'request.form' for Flask.
    """
    return get_post_params().get(field_name, default)


def get_first_query_param(field_name, default=None):
    """ Retrieve the first GET parameter with the specified name
    for the current request.

    This uses 'request.GET' for Pylons and 'request.args' for Flask.
    """
    return get_query_params().get(field_name, default)
