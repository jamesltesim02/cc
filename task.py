#!/bin/python
# -*- coding: utf-8 -*-

import multiprocessing


class Task(object):

    def __init__(self):
        self._queue = multiprocessing.Queue(10)
        #self._subprocess = multiprocessing.Process(target=)
