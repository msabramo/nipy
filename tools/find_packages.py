#!/usr/bin/env python
import os

def main():
    start = os.path.abspath(os.getcwd())
    for root, dirs, files in os.walk(start):
        if '__init__.py' in files:
            print root.replace(start, '').replace(os.path.sep, '.')[1:]
            continue
        pth0, pth1 = os.path.split(root)
        if pth1 in ('tests', 'test'):
            print 'Non-package tests at', root


if __name__ == '__main__':
    main()
