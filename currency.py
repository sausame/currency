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

        def toList(regex, content, func):

            matches = re.finditer(regex, content, re.MULTILINE)

            values = list()

            for match in matches:
                value = func(match.group())

                if value is None:
                    raise Exception('内容不合法：{}'.format(value))

                values.append(value)

            return values

        # Currencies
        self.currencies = toList(r'\s*\d+(\.)*\d*', content, str2currency)

        # Operators
        self.operators = toList(r'[\+\-]', content, str2operator)

        if len(self.currencies) != len(self.operators) + 1:
            raise Exception('操作符和货币不匹配：{}'.format(content))

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

