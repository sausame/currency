#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys
import time
import traceback

from currency import CurrencyLooper
from datetime import tzinfo, timedelta, datetime
from utils import getch, getProperty, reprDict, OutputPath, ThreadWritableObject

def run(configfile, name, filename):

    OutputPath.init(configFile)

    thread = ThreadWritableObject(configFile, name)
    thread.start()

    #sys.stdout = thread
    #sys.errout = thread # XXX: Actually, it does NOT work

    try:
        looper = CurrencyLooper(configFile)
        looper.run(filename)

        #CurrencyLooper.autorun()

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print('Error occurs at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        traceback.print_exc(file=sys.stdout)

    thread.quit()
    thread.join()

if __name__ == '__main__':

    try:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    except:
        pass

    if len(sys.argv) < 3:
        print('Usage:\n\t', sys.argv[0], 'config-file filename\n')
        exit()

    os.environ['TZ'] = 'Asia/Shanghai'
    time.tzset()

    name = os.path.basename(sys.argv[0])[:-3] # Remove ".py"

    configFile = sys.argv[1]
    filename = sys.argv[2]

    run(configFile, name, filename)

