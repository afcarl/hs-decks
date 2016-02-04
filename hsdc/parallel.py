# Shamelessly ripped from http://scottsievert.github.io/blog/2014/07/30/simple-python-parallelism/

from multiprocessing import cpu_count
from multiprocessing import Pool


def parallelize(f, worker_count=cpu_count()):
    """Trivially parallelizes a function"""
    def easy_parallelize(f, sequence):
        """ assumes f takes sequence as input, easy w/ Python's scope """
        pool = Pool(processes=worker_count) # depends on available cores
        result = pool.map(f, sequence) # for i in sequence: result[i] = f(i)
        cleaned = [x for x in result if not x is None] # getting results
        pool.close() # not optimal! but easy
        pool.join()
        return cleaned
    from functools import partial
    return partial(easy_parallelize, f)
