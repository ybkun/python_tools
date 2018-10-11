#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/2/27 15:59
# @Author  : 梁浩晨
# @File    : timer_wrapper.py
# @Software: PyCharm

from decimal import Decimal
from functools import wraps
import time


def format_used_time(st, ed):
    return Decimal(str(ed-st)).quantize(Decimal('0.000'))


def timer(func):
    @wraps(func)
    def func_timer(*args, **kwargs):
        st = time.time()
        ret = func(*args, **kwargs)
        ed = time.time()
        print("call {}, used {} s".format(func.__name__, format_used_time(st, ed)))
        return ret
    return func_timer


if __name__ == '__main__':
    print('test timer wrapper')
    
    @timer
    def foo(a, b):
        sum = a + b
        time.sleep(3)
        print('sum is {}'.format(sum))
        return sum
    
    foo(1, 2)
