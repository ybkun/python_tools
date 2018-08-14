#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/14 10:36
# @Author  : 梁浩晨
# @File    : RW_lock.py
# @Software: PyCharm

from threading import Lock


class RWLock(object):
    def __init__(self):
        self.rlock = Lock()
        self.wlock = Lock()

        self.reader = 0

    @property
    def read_context(self):
        return _ReadLock(self)

    @property
    def write_context(self):
        return _WriteLock(self)


class MyBaseLock(object):
    def acquire(self):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError


class _ReadLock(MyBaseLock):
    def __init__(self, rw_lock: RWLock):
        self._rw_lock = rw_lock

    def acquire(self):
        with self._rw_lock.wlock:  # 等待writer释放锁
            self._rw_lock.reader += 1
            if self._rw_lock.reader == 1:
                self._rw_lock.rlock.acquire()

    def release(self):
        self._rw_lock.reader -= 1
        if self._rw_lock.reader == 0:
            self._rw_lock.rlock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class _WriteLock(MyBaseLock):
    def __init__(self, rw_lock: RWLock):
        self._rw_lock = rw_lock

    def acquire(self):
        self._rw_lock.wlock.acquire()  # 禁止新的reader进入
        self._rw_lock.rlock.acquire()  # 等待现有reader全部退出

    def release(self):
        self._rw_lock.rlock.release()
        self._rw_lock.wlock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


# TEST
if __name__ == '__main__':
    from threading import Thread
    import time
    import random
    global_int = 0
    rw_lock = RWLock()

    def task_reader(rid):
        while True:
            with rw_lock.read_context:
                print('reader {}: {}  -- {}'.format(rid, global_int, time.ctime()))
            time.sleep(1 + random.random())

    def task_writter(wid):
        global global_int
        while True:
            with rw_lock.write_context:
                to_add = random.choice([1, -1])
                new_value = global_int + to_add
                print("writter {}: {}->{}  -- {}".format(wid, global_int, new_value, time.ctime()))
                global_int = new_value
            time.sleep(1.5 + random.random())

    for i in range(3):
        Thread(target=task_reader, args=(i, )).start()

    for i in range(2):
        Thread(target=task_writter, args=(i, )).start()

