# coding: utf-8

from __future__ import unicode_literals
from contextlib import contextmanager
import os
import shutil
import sys
import struct
import collections
import ctypes
import ast

import multiprocessing
import threading

try:
    import queue
except:
    import Queue as queue

try:
    UNICODE_EXISTS = bool(type(unicode))  # Python 2.x
except:
    UNICODE_EXISTS = False  # Python 3.x
try:
    LONG_EXISTS = bool(type(long))  # Python 2.x
except:
    LONG_EXISTS = False  # Python 3.x


def evalStr(s):
    try:
        v = ast.literal_eval(s)
    except ValueError as e:
        raise ValueError("Fail to eval: {0}, {1}".format(s, e))
    return v


def RAW_INPUT(s):
    try:
        return raw_input(s)  # Python 2.x
    except:
        return input(s)  # Python 3.x


def isPython32Bit():
    """
    isPython32Bit()

    :return: True if the current Python interpreter is in 32bit
    """
    return struct.calcsize("P") * 8 == 32

def isPython64Bit():
    """
    isPython64Bit()

    :return: True if the current Python interpreter is in 64bit
    """
    return struct.calcsize("P") * 8 == 64

def isPython2():
    """
    isPython2()

    :return: True is the current Python interpreter is Python 2
    """
    return sys.version_info.major == 2

def isPython3():
    """
    isPython3()

    :return: True is the current Python interpreter is Python 2
    """
    return sys.version_info.major == 3

def handleBytes():
    return not isinstance(b'', str)


def isStringOrUnicode(s):
    return isinstance(s, str) or (UNICODE_EXISTS and isinstance(s, unicode))

def strEncode(s):
    return str.encode(s) if isinstance(s, str) else unicode.encode(s)

def castStr(s):
    return unicode(s) if UNICODE_EXISTS else str(s)

def getErrorMsg(e):
    if hasattr(e, 'message'):
        return castStr(e.message)
    elif hasattr(e, 'msg'):
        return castStr(e.msg)
    else:
        return castStr(e)

def getModulePath(aModule):
    if UNICODE_EXISTS:
        aPath = bytes(aModule.__file__)
    else:
        aPath = bytes(aModule.__file__, sys.getfilesystemencoding())
    return aPath.decode(sys.getfilesystemencoding())

def getAbsPathFromModule(aModule, aRelPath):
    aPath = getModulePath(aModule)
    return os.path.normpath(os.path.abspath(os.path.join(os.path.split(aPath)[0], aRelPath)))

def encodeCommandForSubProcess(cmdList):
    return [arg.encode(sys.getfilesystemencoding()) for arg in cmdList] if isPython2() else cmdList


def isIntOrLong(s):
    if isinstance(s, str):
        try:
            s = int(s)
        except ValueError:
            return False
    return isinstance(s, int) or (LONG_EXISTS and isinstance(s, long))

def isSequence(x):
    return isinstance(x, collections.Sequence)

def iterEnum(enum):
    for name, value in sorted(vars(enum).items()):
        if not name.startswith("__"):
            yield value

@contextmanager
def createTempFolders(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        yield path
    finally:
        shutil.rmtree(path)

def createFolderIfNotExists(aPath):
    """
    createFolderIfNotExists(aPath)
    Create the given tree if it does not already exists

    :param aPath: The path of the folder to create
    :type aPath: str
    """
    if not os.path.exists(aPath):
        os.makedirs(aPath)


def ctypesStringBuffer(aString):
    if isPython2():
        return ctypes.create_string_buffer(aString)
    elif isPython3():
        return ctypes.create_string_buffer(bytes(aString, encoding=sys.getfilesystemencoding()))
    else:
        raise BaseException('Unsupported python major version %d' % sys.version_info.major)



def _worker(taskQueue):
    """
    Thread worker. Grab a task from a queue and run it.

    :param taskQueue: the queue to pull jobs from
    :type taskQueue: queue.Queue
    """
    while not taskQueue.empty():
        try:
            job = taskQueue.get_nowait()
            job()
        except queue.Empty:
            return

def processQueue(taskQueue, nbThreads):
    """
    Process the given queue of tasks with multi threading.

    :param taskQueue: the queue to pull jobs from
    :param nbThreads: number of threads to use to process the queue
    :type taskQueue: queue.Queue
    :type nbThreads: int
    """
    # Initialize the threads
    threads = []
    for i in range(0, min(multiprocessing.cpu_count(), nbThreads)):
        t = threading.Thread(target=_worker, args=[taskQueue])
        threads.append(t)
        t.start()

    # Close the threads
    for t in threads:
        t.join()
