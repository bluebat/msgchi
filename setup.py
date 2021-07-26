from setuptools import setup, find_packages
import io
import codecs
import os
import sys

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'ChangeLog')

setup(
    name='msgchi',
    version=msgchi.__version__,
    url='https://github.com/bluebat/msgchi',
    license='GPL',
    author='Wei-Lun Chao',
    author_email='bluebat@member.fsf.org',
    description='Creating a translation catalog for chinese locales',
    long_description=long_description,
    packages=['msgchi'],
    scripts = ['msgchi.py'],
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 5 - Mature',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Translators',
        'License :: OSI Approved :: GPL',
        'Operating System :: OS Independent',
        'Topic :: Applications',
        ]
)

