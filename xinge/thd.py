#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 23:02:37 2016

@author: yan
"""

import random
from threading import Thread

class MyThread(Thread):
    def __init__(self,thread_id,nums):
        Thread.__init__(self)
        self.thread_id=thread_id
        self.nums=nums
    def run(self):
        for i in self.nums:
            print('In thread ', self.thread_id,' we print ',i)  

l=list(range(10000))
random.shuffle(l)
threads=[]
for i in range(10):
    new_partition=l[i*1000:(i+1)*1000]
    new_thread=MyThread(i,new_partition)
    threads.append(new_thread)
    new_thread.start()

for thread in threads:
    thread.join()

print('We are finished')