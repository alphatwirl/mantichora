[![PyPI version](https://badge.fury.io/py/mantichora.svg)](https://badge.fury.io/py/mantichora)  [![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.2581882.svg)](https://doi.org/10.5281/zenodo.2581882) [![Build Status](https://travis-ci.org/alphatwirl/mantichora.svg?branch=master)](https://travis-ci.org/alphatwirl/mantichora) [![codecov](https://codecov.io/gh/alphatwirl/mantichora/branch/master/graph/badge.svg)](https://codecov.io/gh/alphatwirl/mantichora)

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
- [**Quick start**](#quick-start)
    - [Import libraries](#import-libraries)
    - [Define a task function](#define-a-task-function)
    - [Run tasks concurrently with Mantichora](#run-tasks-concurrently-with-mantichora)
- [**License**](#license)
- [**Contact**](#contact)

*****

## Requirement

- Python 2.7, 3.6, or 3.7
- [atpbar](https://github.com/alphatwirl/atpbar) >= 0.9.7

*****

## Install

You can install Mantichora with `pip`.

```bash
$ pip install -U mantichora
```

*****

## Quick start

I will show here how to use Mantichora by simple examples.

### Import libraries

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

### Define a task function

Let us define a simple task function.

```python
def task_loop(name, ret=None):
    n = random.randint(1000, 100000)
    for i in atpbar(range(n), name=name):
        time.sleep(0.0001)
    return ret
```

The task in this function is to sleep for `0.0001` seconds as many
times as the number randomly selected from between `10000` and
`100000`. `atpbar` is used to show a progress bar. The function takes
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

### Run tasks concurrently with Mantichora

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

## License

- mantichora is licensed under the BSD license.

*****

## Contact

- Tai Sakuma - tai.sakuma@gmail.com
