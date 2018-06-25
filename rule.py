#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Utils
import binascii
import cStringIO
import json
import os
import pprint
import random
import re
import requests
import stat
import string
import sys
import subprocess
import threading
import time
import traceback

from datetime import tzinfo, timedelta, datetime
from utils import getch, getMatchList

class FormulaRule:

    ''' A formula rule contains a formula and several conditions, and number of conditions
        should be more than 1.

        Example: 
            a + b - cd - e; a > 0 && b > 0 && c > 0 && e > 0; a + b > cd && a != e && b != e

        Tips:
            Basic conditions should be the first one, because `eval` will be wrong if a char
            is invalid.
    '''

    def __init__(self, rulefile):
        pass

    def __repr__(self):
        pass

    @staticmethod
    def getFormula(rule):

        def copy(content):
            return content

        lines = rule.split(';')

        formula = lines[0]
        rules = lines[1:]

        chars = getMatchList(r'[a-zA-Z]', formula, copy)
        chars = sorted(set(chars))

        while True:

            formulaDict = dict()

            for ch in chars:
                formulaDict[ch] = '%d' % random.randint(0, 9)

            for rule in rules:

                for key in formulaDict.keys():
                    rule = rule.replace(key, formulaDict[key])

                rule = rule.replace('&&', ' and ').replace('||', ' or ')

                if not eval(rule):
                    break

            else:
                break
       
        for key in formulaDict.keys():
            formula = formula.replace(key, formulaDict[key])

        return formula

