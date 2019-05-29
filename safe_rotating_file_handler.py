#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/29 10:50
# @Author  : 梁浩晨
# @File    : safe_rotating_file_handler.py
# @Software: PyCharm

"""
解决TimedRotatingFileHandler在多线程条件下本地日志丢失的问题
"""

import os
import time
from logging.handlers import TimedRotatingFileHandler
from filelock import FileLock


class MultiprocessRotatingFileHandler(TimedRotatingFileHandler):
    """
    Ref: https://github.com/di/mrfh/blob/master/mrfh/__init__.py
    * 修改doRollover逻辑，避免日志分片时删除已分片日志
    * 释放日志锁时关闭FileStream，解决文件重命名操作被拒绝的问题
    * 频繁reopen FileStream，造成严重的性能损耗
    * 使用FileLock替代threading.Lock，单进程条件下存在性能损失
    """
    def __init__(self, lock_file, *args, **kwargs):
        self.file_lock = FileLock(lock_file)
        super(MultiprocessRotatingFileHandler, self).__init__(*args, **kwargs)

    def _open_file(self):
        self.stream = self._open()

    def acquire(self):
        self.file_lock.acquire()
        if self.stream and self.stream.closed:
            self._open_file()

    def release(self):
        if self.stream and not self.stream.closed:
            self.stream.flush()
            self.stream.close()
        self.file_lock.release()

    def close(self):
        if self.stream and not self.stream.closed:
            self.stream.flush()
            self.stream.close()
        if self.file_lock.is_locked:
            self.file_lock.release()

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        # get the time that this sequence started at and make it a TimeTuple
        current_time = int(time.time())
        dst_now = time.localtime(current_time)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            time_tuple = time.gmtime(t)
        else:
            time_tuple = time.localtime(t)
            dst_then = time_tuple[-1]
            if dst_now != dst_then:
                if dst_now:
                    addend = 3600
                else:
                    addend = -3600
                time_tuple = time.localtime(t + addend)
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(self.suffix, time_tuple))

        # # Changed part
        # if os.path.exists(dfn):
        #     os.remove(dfn)
        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            self.rotate(self.baseFilename, dfn)
        # # Changed part end

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.stream = self._open()
        new_rollover_at = self.computeRollover(current_time)
        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval
        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            if dst_now != dst_at_rollover:
                if not dst_now:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:           # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at






