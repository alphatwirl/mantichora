#!/usr/bin/env python
# Tai Sakuma <tai.sakuma@gmail.com>
import time, random
from atpbar import atpbar
from mantichora import mantichora

##__________________________________________________________________||
def task_loop(name, ret=None):
    n = random.randint(1000, 10000)
    for i in atpbar(range(n), name=name):
        time.sleep(0.0001)
    return ret

result = task_loop('task', 'result')
print(repr(result))

##__________________________________________________________________||
with mantichora(nworkers=3) as mcore:
    mcore.run(task_loop, 'task', ret='result1')
    mcore.run(task_loop, 'another task', ret='result2')
    mcore.run(task_loop, 'still another task', ret='result3')
    mcore.run(task_loop, 'yet another task', ret='result4')
    mcore.run(task_loop, 'task again', ret='result5')
    mcore.run(task_loop, 'more task', ret='result6')
    results = mcore.returns()

print(results)

##__________________________________________________________________||
