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

def seconds2Datetime(seconds):
    #return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seconds))
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S')

def datetime2Seconds(dt):
    return time.mktime(datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').timetuple())
    # return (datetime.strptime(dt, '%Y-%m-%d %H:%M:%S') - datetime(1970, 1, 1)).total_seconds() # XXX CTS

def randomSleep(minS, maxS):
    time.sleep(random.uniform(minS, maxS))

def mkdir(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH):
    if not os.path.exists(path):
        os.mkdir(path, mode)

def chmod(path, mode=stat.S_IRUSR|stat.S_IWUSR|stat.S_IXUSR|stat.S_IRGRP|stat.S_IWGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH):
    if os.path.exists(path):
        os.chmod(path, mode)

try:
    # Win32
    from msvcrt import getch
except ImportError:
    # UNIX
    def getch():
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

def atoi(src):
    if isinstance(src, int):
        return src
    if isinstance(src, str) or isinstance(src, unicode):
        n = 0
        for c in src.lstrip():
            if c.isdigit():
                n *= 10
                n += int(c)
            else:
                break
        return n
    return 0

def toVisibleAscll(src):

    if None == src or 0 == len(src):
        return src

    if unicode != type(src):
        try:
            src = unicode(src, errors='ignore')
        except TypeError, e:
            print 'Unable to translate {!r} of type {}'.format(src, type(src)), ':', e

    dest = ''

    for char in src:
        if char < unichr(32): continue
        dest += char

    return dest

def hexlifyUtf8(src):
    return binascii.hexlify(src.encode('utf-8', 'ignore'))

def unhexlifyUtf8(src):
    return binascii.unhexlify(src).decode('utf-8', 'ignore')

def runCommand(cmd, shell=False):

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output, unused_err = process.communicate()
    retcode = process.poll()

    if retcode is not 0:
        raise subprocess.CalledProcessError(retcode, cmd)

    return retcode

# update property of name to value
def updateProperty(path, name, value):
    fp = None
    targetLine = None
    newLine = None
    try:
        fp = open(path)
        minlen = len(name) + 1
        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue
            group = line.strip().split('=')
            if 2 != len(group) or group[0].strip() != name:
                continue
            if group[1] == value:
                return None
            else:
                targetLine = line
                newLine = '{}={}\r\n'.format(name,value)
                break
    except IOError:
        pass
    finally:
        if fp != None: fp.close()

    if targetLine != None and newLine != None:
        with open(path) as fp:
            content = fp.read()

        content = content.replace(targetLine, newLine)

        with open(path, 'w') as fp:
            fp.write(content)

    return None

def getProperty(path, name):

    fp = None

    try:
        fp = open(path)

        minlen = len(name) + 1

        for line in fp:
            if len(line) < minlen or '#' == line[0]:
                continue

            line = line.strip()
            pos = line.find('=')

            if pos < 0:
                continue

            if line[:pos] != name:
                continue

            return line[pos+1:].strip()

    except IOError:
        pass

    finally:
        if fp != None: fp.close()

    return None

def safePop(obj, name, defaultValue=None):

    try:
        return obj.pop(name)
    except KeyError:
        pass

    return defaultValue

def getMatchString(content, pattern):

    matches = re.findall(pattern, content)

    if matches is None or 0 == len(matches):
        return None

    return matches[0]

def getMatchList(regex, content, func=None):

    matches = re.finditer(regex, content, re.MULTILINE)

    values = list()

    for match in matches:

        if func is not None:
            value = func(match.group())
        else:
            value = match.group()

        if value is None:
            raise Exception('Invalid {}'.format(value))

        values.append(value)

    return values

def dump(obj):

    def dumpObj(obj):

        fields = ['    {}={}'.format(k, v)
            for k, v in obj.__dict__.items() if not k.startswith('_')]

        return ' {}:\n{}'.format(obj.__class__.__name__, '\n'.join(fields))

    if obj is None: return None

    if type(obj) is list:

        for subObj in obj:
            dump(subObj)
    else:
        print dumpObj(obj)

def reprDict(data):
    return json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)

def printDict(obj):
    UniPrinter().pprint(obj)

class UniPrinter(pprint.PrettyPrinter):

    def format(self, obj, context, maxlevels, level):

        if isinstance(obj, unicode):

            out = cStringIO.StringIO()
            out.write('u"')

            for c in obj:
                if ord(c) < 32 or c in u'"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c.encode("utf-8"))

            out.write('"''"')

            # result, readable, recursive
            return out.getvalue(), True, False

        if isinstance(obj, str):

            out = cStringIO.StringIO()
            out.write('"')

            for c in obj:
                if ord(c) < 32 or c in '"\\':
                    out.write('\\x%.2x' % ord(c))
                else:
                    out.write(c)

            out.write('"')

            # result, readable, recursive
            return out.getvalue(), True, False

        return pprint.PrettyPrinter.format(self, obj,
            context, maxlevels, level)

# XXX: Gentlemen should not force ladies to quit but ask them to quit.
class LadyThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            self.runOnce()

            self.mutex.release()

        print 'Quit'

    def runOnce(self):
        raise TypeError('No implement')

    def sleep(self, seconds):

        while self.running and seconds > 0:
            seconds -= 1
            time.sleep(1)

    def quit(self):

        print 'Stopping ...'
        self.running = False

class AutoReleaseThread(threading.Thread):

    def __init__(self):

        self.isInitialized = False

        self.running = True
        threading.Thread.__init__(self)

        self.mutex = threading.Lock()

    def initialize(self):

        try:
            self.mutex.acquire()

            if not self.isInitialized:

                self.isInitialized = True

                self.onInitialized()

            self.accessTime = time.time()

        except KeyboardInterrupt:
            raise KeyboardInterrupt

        finally:
            self.mutex.release()

    def release(self):

        self.isInitialized = False

        self.onReleased()

    def run(self):

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if self.isInitialized:

                diff = time.time() - self.accessTime

                if diff > 30: # 30 seconds
                    self.release()

            self.mutex.release()

            time.sleep(1)

        else:
            self.release()

        print 'Quit'

    def quit(self):

        print 'Stopping ...'
        self.running = False

class OutputPath:

    LOG_OUTPUT_PATH = None
    DATA_OUTPUT_PATH = None

    @staticmethod
    def init(configFile):

        outputPath = getProperty(configFile, 'output-path')
        outputPath = os.path.realpath(outputPath)

        mkdir(outputPath)

        OutputPath.LOG_OUTPUT_PATH = os.path.join(outputPath, 'logs')
        mkdir(OutputPath.LOG_OUTPUT_PATH)

        OutputPath.DATA_OUTPUT_PATH = os.path.join(outputPath, 'datas')
        mkdir(OutputPath.DATA_OUTPUT_PATH)

    @staticmethod
    def getDataPath(key, suffix):
        return '{}/{}.{}'.format(OutputPath.DATA_OUTPUT_PATH, key, suffix)

    @staticmethod
    def clear():

        # Remove data a week ago
        # Data
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 7 * 24 * 3600, '.js')
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 7 * 24 * 3600, '.json')
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 7 * 24 * 3600, '.html')
        removeOverdueFiles(OutputPath.DATA_OUTPUT_PATH, 7 * 24 * 3600, '.png')

class ThreadWritableObject(threading.Thread):

    def __init__(self, configFile, name, log=None):

        threading.Thread.__init__(self)

        self.running = True

        if log is not None:
            self.path = os.path.realpath(log)
        else:
            self.path = os.path.join(OutputPath.LOG_OUTPUT_PATH, '{}.log'.format(name))

        self.contents = []

        self.mutex = threading.Lock()

    def write(self, content):

        self.mutex.acquire()

        self.contents.append(content)

        self.mutex.release()

    def run(self):

        def output(path, contents):

            with open(path, 'a') as fp:

                for content in contents:
                    fp.write(content)

        threadname = threading.currentThread().getName()

        while self.running:

            self.mutex.acquire()

            if 0 != len(self.contents):

                MAX_SIZE = 2*1024*1024

                if os.path.exists(self.path) and os.stat(self.path).st_size > MAX_SIZE:

                    os.rename(self.path, '{}.old'.format(self.path))

                output(self.path, self.contents)

                del self.contents[:]

            self.mutex.release()

            time.sleep(1)

        else:
            output(self.path, self.contents)

    def quit(self):

        print 'Quit ...'
        self.running = False

def removeOverdueFiles(pathname, seconds, suffix=None):

    now = time.time()

    for parent, dirnames, filenames in os.walk(pathname):

        for filename in filenames:

            path = os.path.join(parent, filename)

            if None != suffix and not filename.endswith(suffix):
                continue

            if now > os.path.getctime(path) + seconds:
                # Remove
                os.remove(path)
