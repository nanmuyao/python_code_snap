import time
import os
import sys
import traceback
from datetime import datetime
from gevent import monkey
from io import StringIO
from psycogreen.gevent import patch_psycopg
import logging
from threading import Thread

from django.core.management.base import BaseCommand

from common.helpers import decstr, getLogger, dec

logger = getLogger(__name__)


def t2(args):
    print('t2 args==', args)
    pass


def t1(args):
    print('t1 args==', args)
    pass

def exception_hook(_type, _value, tb):
    from common.helpers import getLogger, CustomJsonFormatter
    print('hookkkkkkk')

    logger = getLogger('exception_hook')
    f = StringIO()
    traceback.print_tb(tb, file=f)
    for handler in logger.handlers:
        handler.setFormatter(CustomJsonFormatter)
    logger.exception(f.getvalue())

def thread_function1(name):

    # 没用
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "exchange_broker.settings")
    #sys.excepthook = exception_hook

    print("Thread %s: starting", name)
    time.sleep(2)
    # 尝试手动捕获异常
    try:
        1/0
    except Exception as e:
        print('catch exception======================')
        from raven.contrib.django.raven_compat.models import client

        client.captureException()
    finally:
        print('finally')
        #sys.excepthook(*sys.exc_info())
    print("Thread %s: finishing", name)

def thread_function2(name):
    print("Thread %s: starting", name)
    time.sleep(2)
    print("Thread %s: finishing", name)


def test_thread():
    # 两种方案1.daemon=False2.join的超时时间长一些
    # Q1 deamon=False 会阻塞主线程吗？
    # Q2 join 时间过长会阻塞主线程吗？
    # A: 取决于任务的执行时间，如果任务while True，那么主线程一直阻塞
    t1 = Thread(target=thread_function1, args=(1,), daemon=True)
    t2 = Thread(target=thread_function2, args=(2,), daemon=True)
    t1.start()
    t2.start()
    print('end1')


    # 这里可以打到centry
    # raise Exception('main thread')
    t1.join(0.1)
    #t2.join(1)

    print('end2')

class Command(BaseCommand):
    """委托单，merge_order, sub_order监控"""

    def handle(self, *args, **options):
        """统计委托单"""
        test_thread()
