import re
from time import time


def process_name(name):
    if name[-3:].lower() == ' nz':
        name = name[:-3]
    return re.sub('[^a-zA-z0-9]+', '', name.lower())


def timeit(label='Unnamed function'):
    def _timeit(f):
        def __timeit(*args, **kwargs):
            start = time()
            ret = f(*args, **kwargs)
            end = time()
            print(f'{label} took {end - start:.4f}s')
            return ret

        return __timeit

    return _timeit
