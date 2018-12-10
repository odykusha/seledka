# -*- coding: utf-8 -*-

import allure
import time
import logging
from requests.exceptions import ReadTimeout, ConnectionError
from functools import wraps
from sqlsoup import Session
from sqlalchemy.exc import (
    OperationalError, IntegrityError, InvalidRequestError
)


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                           CHECKING DECORATOR
# --------------------------------------------------------------------------- #
def TryRequests(fnc):
    u""" Декоратор для перехвата ошибок таймаута и подключения, если такие
    есть, то выполняем запрос(фунцию) еще раз, всего попыток - 3"""
    @wraps(fnc)
    def wrapper(*args, **kwargs):
        try_count = 3

        while try_count > 0:
            try_count -= 1
            try:
                return fnc(*args, **kwargs)
            except ConnectionError:
                allure.attach(
                    u'exception: {err}, '
                    u'def {function}, try: {try_count}'.format(
                        err=u'ConnectionError',
                        function=wrapper.__name__,
                        try_count=try_count
                    ),
                    name='[TryRequests]'
                )

                log.error(
                    u'[TryRequests] exception: {err}, '
                    u'def {function}, try: {try_count}'.format(
                        err=u'ConnectionError',
                        function=wrapper.__name__,
                        try_count=try_count
                    )
                )
                continue
            except ReadTimeout:
                allure.attach(
                    u'exception: {err}, '
                    u'def {function}, try: {try_count}'.format(
                        err=u'ReadTimeout',
                        function=wrapper.__name__,
                        try_count=try_count
                    ),
                    name='[TryRequests]'
                )
                log.error(
                    u'[TryRequests] exception: {err}, '
                    u'def {function}, try: {try_count}'.format(
                        err=u'ReadTimeout',
                        function=wrapper.__name__,
                        try_count=try_count
                    )
                )
                continue
        return fnc(*args, **kwargs)
    return wrapper


def TryInsert(fnc):
    u""" Декоратор для перехвата ошибок инсерта в базу, если такие
    есть, то выполняем запрос(фунцию) еще раз, всего попыток - 3"""
    @wraps(fnc)
    def wrapper(*args, **kwargs):
        try_count = 3

        while try_count > 0:
            try_count -= 1
            try:
                return fnc(*args, **kwargs)
            except InvalidRequestError:
                allure.attach(
                    u'exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'InvalidRequestError',
                        function=wrapper.__name__,
                        try_count=try_count
                    ),
                    name='[TryInsert]'
                )
                log.error(
                    u'[TryInsert] exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'InvalidRequestError',
                        function=wrapper.__name__,
                        try_count=try_count
                    )
                )
                Session.rollback()
                continue
            except IntegrityError:
                allure.attach(
                    u'exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'IntegrityError',
                        function=wrapper.__name__,
                        try_count=try_count
                    ),
                    name='[TryInsert]'
                )
                log.error(
                    u'[TryInsert] exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'IntegrityError',
                        function=wrapper.__name__,
                        try_count=try_count
                    )
                )
                Session.rollback()
                continue
            except OperationalError:
                allure.attach(
                    u'exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'OperationalError',
                        function=wrapper.__name__,
                        try_count=try_count
                    ),
                    name='[TryInsert]'
                )
                log.error(
                    u'[TryInsert] exception: {err}, '
                    u'def {function}, try: {try_count}'
                    u''.format(
                        err=u'OperationalError',
                        function=wrapper.__name__,
                        try_count=try_count
                    )
                )
                Session.rollback()
                continue
        return fnc(*args, **kwargs)
    return wrapper


def TryGetGA(fnc):
    u""" Декоратор для поиска событий в консоли, если результата нет, то
    выполняем запрос(фунцию) еще раз, всего попыток - 3"""
    @wraps(fnc)
    def wrapper(*args, **kwargs):
        try_count = 3

        while try_count > 0:
            try_count -= 1

            result = fnc(*args, **kwargs)
            if result == []:
                log.error(
                    u"[TryGetGA] not found analytics/logs, try: {try_count}"
                    u"".format(
                        try_count=try_count
                    )
                )
                time.sleep(1)
                continue
            else:
                return result

        return fnc(*args, **kwargs)
    return wrapper
