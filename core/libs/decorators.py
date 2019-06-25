
import time
import logging

import allure
from requests.exceptions import ReadTimeout, ConnectionError
from sqlsoup import Session
from sqlalchemy.exc import (
    OperationalError, IntegrityError, InvalidRequestError
)

from functools import wraps


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
                    f'exception: ConnectionError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}',
                    name='[TryRequests]'
                )
                log.error(
                    f'[TryRequests] exception: ConnectionError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}'
                )
                continue
            except ReadTimeout:
                allure.attach(
                    f'exception: ReadTimeout, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}',
                    name='[TryRequests]'
                )
                log.error(
                    f'[TryRequests] exception: ReadTimeout, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}'
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
                    f'exception: InvalidRequestError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}',
                    name='[TryInsert]'
                )
                log.error(
                    f'[TryInsert] exception: InvalidRequestError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}'
                )
                Session.rollback()
                continue
            except IntegrityError:
                allure.attach(
                    f'exception: IntegrityError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}',
                    name='[TryInsert]'
                )
                log.error(
                    f'[TryInsert] exception: IntegrityError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}'
                )
                Session.rollback()
                continue
            except OperationalError:
                allure.attach(
                    f'exception: OperationalError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}',
                    name='[TryInsert]'
                )
                log.error(
                    f'[TryInsert] exception: OperationalError, '
                    f'def {{wrapper.__name__}}, try: {{try_count}}'
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
            if result is list:
                log.error(
                    f"[TryGetGA] not found analytics/logs, try: {{try_count}}"
                )
                time.sleep(1)
                continue
            else:
                return result

        return fnc(*args, **kwargs)
    return wrapper
