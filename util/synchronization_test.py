# -*- coding: utf-8 -*-
"""
Created on 19:31, 02/11/15

@author: wt
"""
from multiprocessing import Process, Lock
from multiprocessing import Process, Value, Array


# def f(l, i):
#     l.acquire()
#     print 'hello world', i
#     l.release()
#
# lock = Lock()
#
# for num in range(10):
#     Process(target=f, args=(lock, num)).start()

def f(n, a):
    n.value = 3.1415927
    for i in range(len(a)):
        a[i] = -a[i]

num = Value('d', 0.0)
arr = Array('i', range(10))
# arr = Array('i', [1, 1, 1, 1, 1])

p1 = Process(target=f, args=(num, arr)).start()
p2 = Process(target=f, args=(num, arr)).start()
# p.start()
# p1.join()
# p2.join()
print num.value
print arr[:]