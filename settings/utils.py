import os


def rel(*x):
    return os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, *x))
