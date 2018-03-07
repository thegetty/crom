from setuptools import setup
import sys

if (sys.version_info[0:2] < (2,7)):
    install_requires =['ordereddict', 'future']
else:
    install_requires = []

setup(
    name = 'cromulent',
    packages = ['cromulent'],
    package_data = {
        'cromulent': ['data/crm_vocab.tsv', 'data/overrides.json', 
        'data/key_order.json', 'data/linked-art.json', 
        'data/cidoc-extension.json', 'data/crm-profile.json']
    },
    test_suite="tests",
    version = '0.9.0',
    description = 'A library for mapping CIDOC-CRM classes to Python objects',
    author = 'Rob Sanderson',
    author_email = 'rsanderson@getty.edu',
    url = 'https://github.com/thegetty/crom',
    install_requires=install_requires,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
