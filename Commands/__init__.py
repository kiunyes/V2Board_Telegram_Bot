#!/usr/bin/env python

import os
import pkgutil

pkgpath = os.path.dirname(__file__)
pkgname = os.path.basename(pkgpath)
for filefinder, name, ispkg in pkgutil.iter_modules([pkgpath]):
    abfile = os.path.join(pkgpath, name)
    __import__(pkgname+'.'+name)
