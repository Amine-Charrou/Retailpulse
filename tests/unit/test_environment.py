import sys

import faker
import numpy
import pandas
import yaml


def test_python_version():
    assert sys.version_info[:2] == (3, 12)


def test_core_dependencies():
    assert faker.Faker
    assert numpy.__version__
    assert pandas.__version__
    assert yaml.__version__
