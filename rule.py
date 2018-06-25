#!/usr/bin/env python
# -*- coding:utf-8 -*-

import random
import re

from utils import getMatchList

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

        self.init(rulefile)

    def __repr__(self):
        pass

    def init(self, rulefile):

        self.index = 0
        self.rules = list()

        try:

            with open(rulefile, 'r') as fp:

                for line in fp.readlines():

                    if '#' == line[0]:
                        continue

                    line = line.strip()

                    if 0 == len(line):
                        continue

                    self.rules.append(line)

        except Exception as e:
            pass

    def reset(self):
        self.index = 0

    def forward(self):

        if self.index + 1 < len(self.rules):
            self.index += 1
            return True

        return False

    def backward(self):

        if self.index > 1:
            self.index -= 1
            return True

        return False

    def createFormula(self):

        if self.index < len(self.rules):
            return FormulaRule.getFormula(self.rules[self.index])

    @staticmethod
    def getFormula(rule):

        lines = rule.split(';')

        formula = lines[0]
        rules = lines[1:]

        chars = getMatchList(r'[a-zA-Z]', formula)
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
