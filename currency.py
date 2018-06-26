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
from rule import FormulaRule
from utils import getch, getMatchList

class CurrencyException(Exception):

    def __init___(self, dErrorArguments):
        Exception.__init__(self, dErrArguments)
        self.dErrorArguments = dErrorArguements

class Operator:

    OPERATOR_ADD = 1
    OPERATOR_MINUS = 2

class Currency:

    def __init__(self, yuan=0, jiao=0, currency=None):

        self.yuan = yuan
        self.jiao = jiao

        if currency is not None:

            pos = currency.find('.')

            if pos >= 0:
                self.yuan = int(currency[:pos])
                self.jiao = int(currency[pos+1:])
            else:
                self.yuan = int(currency)

    def __repr__(self):

        if self.yuan is not 0:

            if self.jiao is 0:
                return u'{}元'.format(self.yuan)

            return u'{}元{}角'.format(self.yuan, self.jiao)

        elif self.jiao is not 0:
            return u'{}角'.format(self.jiao)

        return u'0元'

    def _add(self, other):

        self.yuan += other.yuan
        self.jiao += other.jiao

        if self.jiao >= 10:
            self.jiao -= 10
            self.yuan += 1

        return self

    def _minus(self, other):

        self.yuan -= other.yuan
        self.jiao -= other.jiao

        if self.jiao < 0:
            self.jiao += 10
            self.yuan -= 1

        return self

    @staticmethod
    def add(aYuan, aJiao, bYuan, bJiao):
        a = Currency(aYuan, aJiao)
        b = Currency(bYuan, bJiao)

        a._add(b)
        return a.yuan, a.jiao

    @staticmethod
    def minus(aYuan, aJiao, bYuan, bJiao):
        a = Currency(aYuan, aJiao)
        b = Currency(bYuan, bJiao)

        a._minus(b)
        return a.yuan, a.jiao

class Formula:

    def __init__(self, content):
        self._parse(content)

    def __repr__(self):

        content = ''

        for i in range(len(self.currencies)):

            if i is not 0:

                operator = self.operators[i-1]

                if Operator.OPERATOR_ADD == operator:
                    content += '+'
                elif Operator.OPERATOR_MINUS == operator:
                    content += '-'

            content += '{}'.format(self.currencies[i])

        return content

    def _parse(self, content):

        def str2currency(string):
            return Currency(currency=string)

        def str2operator(string):
            if '+' == string:
                return Operator.OPERATOR_ADD
            elif '-' == string:
                return Operator.OPERATOR_MINUS

            return None

        try:

            # Currencies
            self.currencies = getMatchList(r'\s*\d+(\.)*\d*', content, str2currency)

            # Operators
            self.operators = getMatchList(r'[\+\-]', content, str2operator)

        except Exception as e:
            raise '内容不合法：{}'.format(content)

        if len(self.currencies) is 0:
            raise CurrencyException('输入错误：{}'.format(content))

        if len(self.currencies) != len(self.operators) + 1:
            raise CurrencyException('操作符和货币不匹配：{}'.format(content))

    @staticmethod
    def parse(content):
        return Formula(content)

    def getResult(self):

        result = self.currencies[0]

        for i in range(len(self.operators)):

            operator = self.operators[i]

            if Operator.OPERATOR_ADD == operator:
                result._add(self.currencies[i+1])
            elif Operator.OPERATOR_MINUS == operator:
                result._minus(self.currencies[i+1])

        return result

class CurrencyLooper:

    def __init__(self):
        pass

    def __repr__(self):
        pass

    def run(self, rulefile):

        def clearScreen():
            os.system('clear')

        formulaRule = FormulaRule(rulefile)

        while True:

            rule = formulaRule.createFormula()

            clearScreen()
            print '\n\n第', (formulaRule.getIndex() + 1), '关，按回车键继续，按其它键跳过。'

            if '\r' == getch():

                clearScreen()

                formula = Formula.parse(rule)
                print '\n\n第', (formulaRule.getIndex() + 1), '关\n\n', formula, '= ?'

                msg = '\n\n请输入答案：'

                for i in range(3):

                    if i is not 0:
                        print '\n\n请再想想？'

                    answer = raw_input(msg)
                    correct = False

                    try:
                        if eval('{} == {}'.format(rule, answer)):
                            correct = True
                    except Exception as e:
                        pass

                    try:
                        answer = Formula.parse(answer)
                        answer = answer.getResult()
                    except CurrencyException as e:
                        pass

                    print '\n\n', formula, '=', answer

                    if correct:
                        print '\n\n回答正确！恭喜你通过第', (formulaRule.getIndex() + 1), '关！'
                        break

                else:

                    print '\n\n可能你不太理解，按任意键看答案吧。'
                    getch()

                    print '\n\n', formula, '=', formula.getResult()

                    print '\n\n按任意键再来一次吧。'
                    getch()

                    continue

                print '按任意键继续'
                getch()

            clearScreen()

            if not formulaRule.forward():
                break

    @staticmethod
    def autorun():

        def clearScreen():
            os.system('clear')

        while True:

            msg = '例如：1元1角 + 2元2角 - 3元, 输入为：1.1 + 2.2 - 3\n请输入式子：\n'
            content = raw_input(msg)

            content.strip()

            if len(content) is 0:
                break

            try:
                clearScreen()

                formula = Formula.parse(content)
                print formula

                print '\n\n按任意键看答案'
                getch()

                result = formula.getResult()
                print '\n\n', result

            except CurrencyException as e:
                print e

            print '按任意键继续'
            getch()

            clearScreen()

