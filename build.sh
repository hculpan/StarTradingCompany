#!/bin/bash
rm -rf build
rm -rf build
python setup.py build
python setup.py bdist_mac
