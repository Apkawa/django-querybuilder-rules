[![Build Status](https://travis-ci.org/Apkawa/django-querybuilder-rules.svg?branch=master)](https://travis-ci.org/Apkawa/django-querybuilder-rules)
[![Coverage Status](https://coveralls.io/repos/github/Apkawa/django-querybuilder-rules/badge.svg)](https://coveralls.io/github/Apkawa/django-querybuilder-rules)
[![codecov](https://codecov.io/gh/Apkawa/django-querybuilder-rules/branch/master/graph/badge.svg)](https://codecov.io/gh/Apkawa/django-querybuilder-rules)
[![Requirements Status](https://requires.io/github/Apkawa/django-querybuilder-rules/requirements.svg?branch=master)](https://requires.io/github/Apkawa/django-querybuilder-rules/requirements/?branch=master)
[![PyUP](https://pyup.io/repos/github/Apkawa/django-querybuilder-rules/shield.svg)](https://pyup.io/repos/github/Apkawa/django-querybuilder-rules)
[![PyPI](https://img.shields.io/pypi/pyversions/django-querybuilder-rules.svg)]()

Project for merging different file types, as example easy thumbnail image and unpacking archive in one field

# Installation

```bash
pip install django-querybuilder-rules

```

or from git

```bash
pip install -e git+https://githib.com/Apkawa/django-querybuilder-rules.git#egg=django-querybuilder-rules
```

## Django and python version

* python-2.7 - django>=1.8,<=1.11
* python-3.4 - django>=1.8,<=1.11
* python-3.5 - django>=1.8,<=1.11
* python-3.6 - django>=1.11


# Usage



# Contributing

## run example app

```bash
pip install -r requirements.txt
./test/manage.py migrate
./test/manage.py runserver
```

## run tests

```bash
pip install -r requirements.txt
pytest
tox
```

## publish pypi

```bash
python setup.py sdist upload -r pypi
```






