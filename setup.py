from setuptools import find_packages, setup
import os.path
import sys


def read_project_version(*py):
    py = os.path.join(*py)
    __version__ = None
    for line in open(py).read().splitlines():
        if '__version__' in line:
            exec(line)
            break
    return __version__

NAME = 'sphinxcontrib-gtkwave'
URL = 'https://github.com/ponty/sphinxcontrib-gtkwave'
DESCRIPTION = 'Sphinx extension to include screenshot of GTKWave'
VERSION = read_project_version('sphinxcontrib', 'gtkwave.py')

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

classifiers = [
    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    'License :: OSI Approved :: BSD License',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Environment :: Console',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Documentation',
    'Topic :: Utilities',
]

install_requires = open('requirements.txt').read().split('\n')

# compatible with distutils of python 2.3+ or later
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open('README.rst', 'r').read(),
    classifiers=classifiers,
    keywords='sphinx screenshot gtkwave vcd',
    author='ponty',
    # author_email='',
    url=URL,
    license='BSD',
    packages=find_packages(exclude=['bootstrap', 'pavement', ]),
    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,
    install_requires=install_requires,
    namespace_packages=['sphinxcontrib'],
    **extra
)
