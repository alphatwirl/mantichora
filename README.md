[![PyPI version](https://badge.fury.io/py/mantichora.svg)](https://badge.fury.io/py/mantichora) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/mantichora/badges/version.svg)](https://anaconda.org/conda-forge/mantichora) [![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2581882.svg)](https://doi.org/10.5281/zenodo.2581882) [![Build Status](https://travis-ci.org/alphatwirl/mantichora.svg?branch=master)](https://travis-ci.org/alphatwirl/mantichora) [![codecov](https://codecov.io/gh/alphatwirl/mantichora/branch/master/graph/badge.svg)](https://codecov.io/gh/alphatwirl/mantichora)

# Mantichora

A simple interface to _multiprocessing_

*****

_Mantichora_ provides a simple interface to
[_multiprocessing_](https://docs.python.org/3/library/multiprocessing.html).

```python
from mantichora import mantichora

with mantichora() as mcore:
    mcore.run(func1)
    mcore.run(func2)
    mcore.run(func3)
    mcore.run(func4)
    results = mcore.returns()
```

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |    12559 /    12559 |:  func1
  71.27% ::::::::::::::::::::::::::::             |    28094 /    39421 |:  func2
  30.34% ::::::::::::                             |    28084 /    92558 |:  func3
  35.26% ::::::::::::::                           |    27282 /    77375 |:  func4
```
 
You can simply give Mantichora as many functions as you need to run.
Mantichora will run them concurrently in background processes by using
multiprocessing and give you the return values of the functions. The
return values are sorted in the order of the functions you have
originally given to Mantichora. Progress bars from
[atpbar](https://github.com/alphatwirl/atpbar) can be used in the
functions.

The code in this package was originally developed in the sub-package
[_concurrently_](https://github.com/alphatwirl/alphatwirl/tree/v0.23.2/alphatwirl/concurrently)
of [_alphatwirl_](https://github.com/alphatwirl/alphatwirl).


The examples in this file can be also run on Jupyter Notebook. <br />
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/alphatwirl/notebook-mantichora-001/master?filepath=mantichora.ipynb)

*****

- [**Requirement**](#requirement)
- [**Install**](#install)
- [**User guide**](#user-guide)
    - [**Quick start**](#quick-start)
        - [Import libraries](#import-libraries)
        - [Define a task function](#define-a-task-function)
        - [Run tasks concurrently with Mantichora](#run-tasks-concurrently-with-mantichora)
    - [**Features**](#features)
        - [Without the `with` statement](#without-the-with-statement)
            - [`end()`](#end)
            - [`terminate()`](#terminate)
        - [Receive results as tasks finish](#receive-results-as-tasks-finish)
            - [`receive_one()`](#receive_one)
            - [`receive_finished()`](#receive_finished)
        - [Logging](#logging)
        - [Start method of multiprocessing](#start-method-of-multiprocessing)
- [**License**](#license)
- [**Contact**](#contact)

*****

## Requirement

- Python 3.6, 3.7, or 3.8

*****

## Install

You can install with `conda` from conda-forge:

```bash
conda install -c conda-forge mantichora
```

or with `pip`:

```bash
pip install -U mantichora
```

## User guide

### Quick start

I will show here how to use Mantichora by simple examples.

#### Import libraries

We are going use two python standard libraries
[time](https://docs.python.org/3/library/time.html) and
[random](https://docs.python.org/3/library/random.html) in an example
task function. In the example task function, we are also going to use
[atpbar](https://github.com/alphatwirl/atpbar) for progress bars.
Import these packages and `mantichora`.

```python
import time, random
from atpbar import atpbar
from mantichora import mantichora
```

#### Define a task function

Let us define a simple task function.

```python
def task_loop(name, ret=None):
    n = random.randint(1000, 10000)
    for i in atpbar(range(n), name=name):
        time.sleep(0.0001)
    return ret
```

The task in this function is to sleep for `0.0001` seconds as many
times as the number randomly selected from between `1000` and
`10000`. `atpbar` is used to show a progress bar. The function takes
two arguments: `name`, the label on the progress bar, and `ret`, the
return value of the function.

**Note:** Mantichora uses
[multiprocessing](https://docs.python.org/3/library/multiprocessing.html)
to run task functions in background processes. As a result, task
functions, their arguments, and their return values need to be
[picklable](https://docs.python.org/3.6/library/pickle.html#what-can-be-pickled-and-unpickled).

You can just try running this function without using Mantichora.

```python
result = task_loop('task1', 'result1')
```

This doesn't return immediately. It waits for the function to finish.
You will see a progress bar.

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |    58117 /    58117 |:  task1
```

The return value is stored in `result`.

```python
print(result)
```

```
 'result1'
```

#### Run tasks concurrently with Mantichora

Now, we run multiple tasks concurrently with Mantichora.

```python
with mantichora(nworkers=3) as mcore:
    mcore.run(task_loop, 'task', ret='result1')
    mcore.run(task_loop, 'another task', ret='result2')
    mcore.run(task_loop, 'still another task', ret='result3')
    mcore.run(task_loop, 'yet another task', ret='result4')
    mcore.run(task_loop, 'task again', ret='result5')
    mcore.run(task_loop, 'more task', ret='result6')
    results = mcore.returns()
```

In the example code above, `mantichora` is initialized with an
optional argument `nworkers`. The `nworkers` specifies the number of
the workers. It is `3` in the above example. The default is `4`. At
most as many tasks as `nworkers` can run concurrently.

The [`with`
statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
is used in the example. This ensures that `mantichora` properly
ends the workers.

You can give task functions and their arguments to `mcore.run()`. You
can call `mcore.run()` as many times as you need. In the above
example, `mcore.run()` is called with the same task function with
different arguments. You can also use a different function each time.
`mcore.run()` returns immediately; it doesn't wait for the task to
finish or even to start. In each call, `mcore.run()` only puts a task
in a queue. The workers in background processes pick up tasks from the
queue and run them.

The `mcore.returns()` waits until all tasks finish and returns their
return values, which are sorted in the order of the tasks you have
originally given to `mcore.run()`.

Progress bars will be shown by `atpbar`.

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     1415 /     1415 |:  still another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     7770 /     7770 |:  task again
 100.00% :::::::::::::::::::::::::::::::::::::::: |    18431 /    18431 |:  yet another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |    25641 /    25641 |:  more task
 100.00% :::::::::::::::::::::::::::::::::::::::: |    74669 /    74669 |:  task
 100.00% :::::::::::::::::::::::::::::::::::::::: |    87688 /    87688 |:  another task
```

The results are sorted in the original order regardless of the order
in which the tasks have finished.

```python
print(results)
```

```
['result1', 'result2', 'result3', 'result4', 'result5', 'result6']
```
 
*****

### Features

#### Without the `with` statement

##### `end()`

If you don't use the `with` statement, you need to call `end()`.

```python
mcore = mantichora()

mcore.run(task_loop, 'task', ret='result1')
mcore.run(task_loop, 'another task', ret='result2')
mcore.run(task_loop, 'still another task', ret='result3')
mcore.run(task_loop, 'yet another task', ret='result4')
mcore.run(task_loop, 'task again', ret='result5')
mcore.run(task_loop, 'more task', ret='result6')

results = mcore.returns()

mcore.end()
print(results)
```

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     4695 /     4695 |:  yet another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     7535 /     7535 |:  still another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     9303 /     9303 |:  another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     9380 /     9380 |:  task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     5812 /     5812 |:  more task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     9437 /     9437 |:  task again
['result1', 'result2', 'result3', 'result4', 'result5', 'result6']
```

##### `terminate()`

`mantichora` can be terminated with `terminate()`. After `terminate()`
is called, `end()` still needs to be called. In the example below,
`terminate()` is called after 0.5 seconds of sleep while some tasks
are still running.

```python
mcore = mantichora()

mcore.run(task_loop, 'task', ret='result1')
mcore.run(task_loop, 'another task', ret='result2')
mcore.run(task_loop, 'still another task', ret='result3')
mcore.run(task_loop, 'yet another task', ret='result4')
mcore.run(task_loop, 'task again', ret='result5')
mcore.run(task_loop, 'more task', ret='result6')

time.sleep(0.5)

mcore.terminate()
mcore.end()
```

The progress bars stop when the tasks are terminated.

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     2402 /     2402 |:  still another task
 100.00% :::::::::::::::::::::::::::::::::::::::: |     3066 /     3066 |:  another task
  59.28% :::::::::::::::::::::::                  |     2901 /     4894 |:  task
  69.24% :::::::::::::::::::::::::::              |     2919 /     4216 |:  yet another task
   0.00%                                          |        0 /     9552 |:  task again
   0.00%                                          |        0 /     4898 |:  more task
```

*****

#### Receive results as tasks finish

Instead of waiting for all tasks to finish beofre receiving the
reulsts, you can get results as tasks finish with the method
`receive_one()` or `receive_receive()`.

#### `receive_one()`

The method `receive_one()` returns a pair of the run ID and the return
value of a task function. If no task has finished, `receive_one()`
waits until one task finishes. `receive_one()` returns `None` if no
tasks are outstanding. The method `run()` returns the run ID for the
task.

```python
with mantichora() as mcore:
    runids = [ ]
    runids.append(mcore.run(task_loop, 'task1', ret='result1'))
    runids.append(mcore.run(task_loop, 'task2', ret='result2'))
    runids.append(mcore.run(task_loop, 'task3', ret='result3'))
    runids.append(mcore.run(task_loop, 'task4', ret='result4'))
    runids.append(mcore.run(task_loop, 'task5', ret='result5'))
    runids.append(mcore.run(task_loop, 'task6', ret='result6'))
    #
    pairs = [ ]
    for i in range(len(runids)):
        pairs.append(mcore.receive_one())
```

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     1748 /     1748 |:  task3
 100.00% :::::::::::::::::::::::::::::::::::::::: |     4061 /     4061 |:  task1
 100.00% :::::::::::::::::::::::::::::::::::::::: |     2501 /     2501 |:  task5
 100.00% :::::::::::::::::::::::::::::::::::::::: |     2028 /     2028 |:  task6
 100.00% :::::::::::::::::::::::::::::::::::::::: |     8206 /     8206 |:  task4
 100.00% :::::::::::::::::::::::::::::::::::::::: |     9157 /     9157 |:  task2
```

The `runid` is the list of the run IDs in the order of the tasks that
have been given to `run()`.

```python
print(runids)
```

```
[0, 1, 2, 3, 4, 5]
```

The `pairs` are in the order in which the tasks have finished.

```python
print(pairs)
```

```
[(2, 'result3'), (0, 'result1'), (4, 'result5'), (5, 'result6'), (3, 'result4'), (1, 'result2')]
```

##### `receive_finished()`

The method `receive_finished()` returns a list of pairs of the run ID
and the return value of finished task functions. The method
`receive_finished()` doesn't wait for a task to finish. It returns an
empty list if no task has finished.

```python
with mantichora() as mcore:
    runids = [ ]
    runids.append(mcore.run(task_loop, 'task1', ret='result1'))
    runids.append(mcore.run(task_loop, 'task2', ret='result2'))
    runids.append(mcore.run(task_loop, 'task3', ret='result3'))
    runids.append(mcore.run(task_loop, 'task4', ret='result4'))
    runids.append(mcore.run(task_loop, 'task5', ret='result5'))
    runids.append(mcore.run(task_loop, 'task6', ret='result6'))
    #
    pairs = [ ]
    while len(pairs) < len(runids):
        pairs.extend(mcore.receive_finished())
```

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     3979 /     3979 |:  task3
 100.00% :::::::::::::::::::::::::::::::::::::::: |     6243 /     6243 |:  task2
 100.00% :::::::::::::::::::::::::::::::::::::::: |     6640 /     6640 |:  task1
 100.00% :::::::::::::::::::::::::::::::::::::::: |     8632 /     8632 |:  task4
 100.00% :::::::::::::::::::::::::::::::::::::::: |     6235 /     6235 |:  task5
 100.00% :::::::::::::::::::::::::::::::::::::::: |     8325 /     8325 |:  task6
```

The `runid` is again the list of the run IDs in the order of the tasks
that have been given to `run()`.

```python
print(runids)
```

```
[0, 1, 2, 3, 4, 5]
```

The `pairs` are also again in the order in which the tasks have finished.

```python
print(pairs)
```

```
[(2, 'result3'), (1, 'result2'), (0, 'result1'), (3, 'result4'), (4, 'result5'), (5, 'result6')]
```

*****

#### Logging

Logging in background processes is propagated to the main process in
the way described in a [section of Logging
Cookbook](https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes).

Here is a simple example task function that uses `logging`. The task
function does logging just before returning.


```python
import logging

def task_log(name, ret=None):
    n = random.randint(1000, 10000)
    for i in atpbar(range(n), name=name):
        time.sleep(0.0001)
    logging.info('finishing "{}"'.format(name))
    return ret
```

Set the logging stream to a string stream so that we can later
retrieve the logging as a string.

```python
import io
stream = io.StringIO()
logging.basicConfig(level=logging.INFO, stream=stream)
```

Run the tasks.

```python
with mantichora() as mcore:
    mcore.run(task_log, 'task1', ret='result1')
    mcore.run(task_log, 'task2', ret='result2')
    mcore.run(task_log, 'task3', ret='result3')
    mcore.run(task_log, 'task4', ret='result4')
    results = mcore.returns()
```

```
 100.00% :::::::::::::::::::::::::::::::::::::::: |     4217 /     4217 |:  task2
 100.00% :::::::::::::::::::::::::::::::::::::::: |     7691 /     7691 |:  task3
 100.00% :::::::::::::::::::::::::::::::::::::::: |     8140 /     8140 |:  task1
 100.00% :::::::::::::::::::::::::::::::::::::::: |     9814 /     9814 |:  task4
```

Logging made in the task function in background processes is sent to
the main process and written in the string stream.


```python
print(stream.getvalue())
```

```
INFO:root:finishing "task2"
INFO:root:finishing "task3"
INFO:root:finishing "task1"
INFO:root:finishing "task4"
```

*****

#### Start method of multiprocessing

Python multiprocessing has three start methods: `spawn`, `fork`, `forkserver`.
Each method is described in the Python
[documentation](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods).
Mantichora uses the `fork` method by default. You can change the method by the
option `mp_start_method`. For example, to use the `spawn` method,

```python
mantichora(mp_start_method='spawn')
```

- On Jupyter Notebook, the `fork` method is typically the best choice.
- The `spawn` and `forkserver` methods have extra restrictions, for
  example, on how the main module is written. The restrictions are
  described in the Python
  [documentation](https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods).
- On MacOS, in the `fork` method, errors with the message `may have
  been in progress in another thread when fork() was called` might
  occur. This error might be resolved if the environment variable
  `OBJC_DISABLE_INITIALIZE_FORK_SAFETY` is set `YES` as suggested at
  [Stack Overflow](https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr).


*****

## License

- mantichora is licensed under the BSD license.

*****

## Contact

- Tai Sakuma - tai.sakuma@gmail.com
