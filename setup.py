from setuptools import setup, find_packages
import versioneer

from pathlib import Path

here = Path(__file__).resolve().parent
long_description = here.joinpath('README.md').read_text()

setup(
    name='mantichora',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A simple interface to multiprocessing and threading',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Tai Sakuma',
    author_email='tai.sakuma@gmail.com',
    url='https://github.com/alphatwirl/mantichora',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'atpbar>=1.0.8'
    ],
    extras_require={
        'tests': [
            'pytest>=5.4',
            'pytest-cov>=2.8',
            'pytest-console-scripts>=0.2',
        ],
    }
)
