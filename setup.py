from setuptools import setup, Command
from pip.req import parse_requirements
import pip
from os import path

cwd = path.abspath(path.dirname(__file__))

install_reqs = parse_requirements(path.join(cwd,'requirements.txt'), session=pip.download.PipSession())
reqs = [str(ir.req) for ir in install_reqs]

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='dynamite',
    description='Autoscaling Tool for CoreOS',
    version='0.0.0.dev1',
    packages=['dynamite', 'dynamite.INIT', 'dynamite.tests', 'dynamite.tests.INIT', 'dynamite.GENERAL'],
    url='https://github.com/sandorkan/dynamite',
    license='Apache License 2.0',
    author='brnr',
    author_email='brnr@zhaw.ch',
    install_requires=reqs,
    tests_require=['pytest'],
    cmdclass={'test': PyTest},

    classifiers=[
        # Availale Classifiers --> https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Information Technology',
        'Topic :: Utilities',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.4'
        ]
)