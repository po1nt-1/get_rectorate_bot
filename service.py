import inspect
import os
import sys


class Local_Error(Exception):
    pass


def _get_script_dir(follow_symlinks=True):
    '''получить директорию со скриптом'''

    # https://clck.ru/P8NUA
    if getattr(sys, 'frozen', False):
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(_get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


def path_to(file_name):
    return os.path.join(_get_script_dir(), str(file_name))
