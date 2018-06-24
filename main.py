#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from currency import Currency, Formula
from datetime import tzinfo, timedelta, datetime
from utils import getchar, getProperty, reprDict, OutputPath, ThreadWritableObject

def autorun():

    def clearScreen():

        for i in range(50):
            print '\n'

    while True:

        msg = '例如：1元1角 + 2元2角 - 3元, 输入为：1.1 + 2.2 - 3\n请输入式子：\n'
        content = raw_input(msg)

        content.strip()

        if len(content) is 0:
            break

        clearScreen()

        formula = Formula.parse(content)
        print formula

        print '\n\n按任意键看答案'
        sys.stdin.read(1)

        result = formula.getResult()
        print result

        print '按任意键继续'
        sys.stdin.read(1)

        clearScreen()

def run(configfile, name):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    #sys.stdout = thread
    #sys.errout = thread # XXX: Actually, it does NOT work

    try:

        autorun()

        a = Currency(12)
        b = Currency(1, 4)

        print a, '+', b, '=', a._add(b)
        #print Currency.add(1, 2, 3, 4)
        #print Currency.minus(3, 4, 1, 2)

    except KeyboardInterrupt:
        pass
    except Exception, e:
        print 'Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        traceback.print_exc(file=sys.stdout)

    thread.quit()
    thread.join()

if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding('utf-8')

    if len(sys.argv) < 2:
        print 'Usage:\n\t', sys.argv[0], 'config-file\n'
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"

    configFile = sys.argv[1]

    run(configFile, name)

