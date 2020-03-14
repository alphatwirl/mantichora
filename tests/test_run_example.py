# Tai Sakuma <tai.sakuma@gmail.com>
"""Test if an example script runs

"""

import os

import pytest

here = os.path.abspath(os.path.dirname(__file__))
example_dir = os.path.abspath(os.path.join(here, '..', 'examples'))
example_script_path = os.path.join(example_dir, 'example_01.py')

##__________________________________________________________________||
@pytest.mark.script_launch_mode('subprocess')
def test_run_example_script(script_runner):
    ret = script_runner.run(example_script_path)
    pass

##__________________________________________________________________||
