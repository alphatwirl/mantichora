# Changelog

## [Unreleased]

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.10.0...master))
## [0.10.0] - 2020-03-28

**PyPI**: https://pypi.org/project/mantichora/0.10.0/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.9...v0.10.0))
- added `threading` mode, which can be selected by new option `mode`
- added brief sleeps in "while" loops, which improves performance in some circumstances
- removed code for Python 2.7

## [0.9.9] - 2020-03-28

**PyPI**: https://pypi.org/project/mantichora/0.9.9/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.8...v0.9.9))
- added option `mp_start_method`
    - users can choose the [start method](https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods) of `multiprocessing` from three options: `fork`, `spawn`, and `forkserver`
    - addressing the issue #4 comment [599216616](https://github.com/alphatwirl/mantichora/issues/4#issuecomment-599216616)

## [0.9.8] - 2020-03-14

**PyPI**: https://pypi.org/project/mantichora/0.9.8/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.7...v0.9.8))
- stopped supporting Python 2.7
- updated to use the "fork" multiprocessing start method, addressing the issue [#4](https://github.com/alphatwirl/mantichora/issues/4)

## [0.9.7] - 2020-02-15

**PyPI**: https://pypi.org/project/mantichora/0.9.7/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.6...v0.9.7))
- added tests on Python 3.8 in Travis CI

## [0.9.6] - 2020-02-15

**PyPI**: https://pypi.org/project/mantichora/0.9.6/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.5...v0.9.6))
- cleaned code
- fixed a bug in which the logging level was not effective
- added a new class `ThreadingHub`

## [0.9.5] - 2019-03-15

**PyPI**: https://pypi.org/project/mantichora/0.9.5/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.4...v0.9.5))
- updated `README.md`, `setup.py`

## [0.9.4] - 2019-03-14

**PyPI**: https://pypi.org/project/mantichora/0.9.4/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.3...v0.9.4))
- updated `README.md`, docstrings
- cleaned up code

## [0.9.3] - 2019-03-10

**PyPI**: https://pypi.org/project/mantichora/0.9.3/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.2...v0.9.3))
- added `receive_one()`, `receive_finished()`
- changed the behavior:
    - `mantichora` no longer waits all tasks to finish at exit of the
      `with` statement. It terminates all workers.
- updated required `atpbar` version from 0.9.7 to 1.0.2
- updated `README.md`, `MANIFEST.in`, `setup.py`, tests
- cleaned up code

## [0.9.2] - 2019-03-02

**PyPI**: https://pypi.org/project/mantichora/0.9.2/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.1...v0.9.2))
- updated `README.md`

## [0.9.1] - 2019-03-02

**PyPI**: https://pypi.org/project/mantichora/0.9.1/

#### Changes from the previous release: ([diff](https://github.com/alphatwirl/mantichora/compare/v0.9.0...v0.9.1))
- updated the development status to Beta in `setup.py`
- updated `README.md`

## [0.9.0] - 2019-03-02

**PyPI**: https://pypi.org/project/mantichora/0.9.0/
