#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 23:02:37 2016

@author: yan
"""

import random
from threading import Thread
from queue import Queue

l=list(range(10000))

q=Queue()
for item in l:
    q.put(item)


class MyThread(Thread):
    def __init__(self,thread_id):
        Thread.__init__(self)
        self.thread_id=thread_id
    def run(self):
        while True:
            item=q.get()
            if item is None:
                break
            print('In thread ', self.thread_id,' we print ',item)
            q.task_done()

threads=[]

for i in range(10):
    q.put(None)
for i in range(10):
    new_thread=MyThread(i)
    threads.append(new_thread)
    new_thread.start()

for thread in threads:
    thread.join()

print('We are finished')