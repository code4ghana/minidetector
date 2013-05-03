#!/usr/bin/python
from distutils.core import setup

setup(
    name='minidetector',
    version='1.3.1',
    description='Django middleware and view decorator to detect phones and small-screen devices',
    long_description = '',
    author='metamoof, Chris Drackett, Steve Schwarz, Andrew MacKinlay',
    url = "http://github.com/admackin/minidetector",
    package_dir={'': 'src'},
    packages = [
        "minidetector",
        "minidetector.tests",
    ],
    package_data={
        'minidetector': ['search_strings.txt'],
        'minidetector.tests': ['*.txt'],
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
