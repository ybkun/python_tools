#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/11 16:44
# @Author  : 梁浩晨
# @File    : std_logger_setting.py
# @Software: PyCharm

import logging
import sys
import os

from logging.handlers import TimedRotatingFileHandler
from logging import StreamHandler
from logging import Formatter

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir, 'log/')

if not os.path.exists(log_dir):
    os.mkdir(log_dir)

default_format = '%(asctime)s|%(threadName)s(%(process)d)|%(name)s - %(levelname)-5s - %(message)s'


def std_setting(logger: logging.Logger,
                level=logging.DEBUG,
                *,
                format_str: str=None,
                log_file: str=None,
                when_separate='midnight'):
    # 清空handler, 以免重复输出
    if logger.hasHandlers():
        for hdlr in logger.handlers.copy():
            logger.removeHandler(hdlr)

    # set formatter
    if not format_str:
        format_str = default_format
    formatter = Formatter(format_str)

    # set stream handler
    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)

    # set file handler
    if log_file:
        file_handler = TimedRotatingFileHandler(os.path.join(log_dir, log_file),
                                                when=when_separate,
                                                encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    logger.setLevel(level)


std_loggers = {}


def std_logger(name):
    global std_loggers

    if name not in std_loggers:
        file_name = '{}.log'.format(name)
        logger = logging.getLogger(name)
        std_setting(logger, log_file=file_name)
        std_loggers[name] = logger

    return std_loggers[name]
