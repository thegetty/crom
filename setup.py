from setuptools import setup, find_packages

setup(
    name = 'crmpy',
    packages = find_packages(),
    test_suite="test",
    version = '0.0.1',
    description = 'A library for mapping CIDOC-CRM classes to Python objects',
    author = 'Getty Research Institute',
    author_email = 'jgomez@getty.edu',
    url = 'https://github.com/gri-is/crmpy',
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache License",
        "Development Status :: pre-Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
