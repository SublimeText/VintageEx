"""
This module lists error codes and error display messages along with
utilities to handle them.
"""

import sublime


ERR_UNKNOWN_COMMAND = 492
ERR_TRAILING_CHARS = 488
ERR_NO_BANG_ALLOWED = 477
ERR_INVALID_RANGE = 16
ERR_NO_RANGE_ALLOWED = 481


ERR_MESSAGES = {
    ERR_TRAILING_CHARS: 'Traling characters.',
    ERR_UNKNOWN_COMMAND: 'Not an editor command.',
    ERR_NO_BANG_ALLOWED: 'No ! allowed.',
    ERR_INVALID_RANGE: 'Invalid range.',
    ERR_NO_RANGE_ALLOWED: 'No range allowed.'
}


def get_error_message(error_code):
    return ERR_MESSAGES.get(error_code, '')


def display_error(error_code, arg='', log=False):
    err_fmt = "VintageEx: E%d %s"
    if arg:
        err_fmt += " (%s)" % arg
    msg = get_error_message(error_code)
    sublime.status_message(err_fmt % (error_code, msg))
    
