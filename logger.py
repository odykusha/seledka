
import py
import logging
from datetime import datetime

import allure


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                  Check errors from browser (in console)
# --------------------------------------------------------------------------- #
# шаблоны сообщений, которых игнорировать в консоле браузера
SKIPPED_ERRORS = [
    "see https://fb.me",
    "This content should also be served over HTTPS.",
]


def major_errors(console_error):
    u""" проверка что логи не помемечены, как скипнутые, см. SKIPPED_ERRORS """
    for template_err in SKIPPED_ERRORS:
        if template_err in console_error:
            return False
    return True


def check_console_error(driver):
    u""" Поиск всех ошибок которые были найдены в консоли """
    # found browser logs
    browser_log_list = []
    uniq_message = []
    for lg in driver.get_log('browser'):
        if lg['message'] not in uniq_message and major_errors(lg['message']):
            uniq_message.append(lg['message'])
            found_log = "{time} {level}[{source}]\t{message}".format(
                time=datetime.fromtimestamp(
                    lg['timestamp'] / 1000).strftime('%H:%M:%S'),
                level=lg.get('level'),
                source=lg.get('source'),
                message=lg.get('message')
            )
            browser_log_list.append(found_log)
            log.warning(found_log)
    if browser_log_list:
        allure.attach(
            '\n'.join(browser_log_list),
            name='log[browser]',
            attachment_type=allure.attachment_type.JSON
        )

    # found driver logs
    driver_log_list = []
    uniq_message = []
    for lg in driver.get_log('driver'):
        if lg['message'] not in uniq_message:
            uniq_message.append(lg['message'])
            found_log = "{time} {level}[{source}]\t{message}".format(
                time=datetime.fromtimestamp(
                    lg['timestamp'] / 1000).strftime('%H:%M:%S'),
                level=lg.get('level'),
                source=lg.get('source'),
                message=lg.get('message')
            )
            driver_log_list.append(found_log)
            log.warning(found_log)
    if driver_log_list:
        allure.attach(
            '\n'.join(driver_log_list),
            name='log[driver]',
            attachment_type=allure.attachment_type.JSON
        )


# --------------------------------------------------------------------------- #
#                              Logger Configure
# --------------------------------------------------------------------------- #
class Logger(object):

    def pytest_runtest_setup(self, item):
        # @@@ - разделитель логов
        item.capturelog_handler = LoggerHandler()
        item.capturelog_handler.setFormatter(logging.Formatter(
            "<<%(levelname)s>>%(asctime)s.%(msecs)03d\t%(message)s@@@",
            "%H:%M:%S"
        ))
        root_logger = logging.getLogger()
        root_logger.addHandler(item.capturelog_handler)
        root_logger.setLevel(logging.NOTSET)

    def pytest_runtest_makereport(self, __multicall__, item, call):  # noqa

        report = __multicall__.execute()

        if hasattr(item, "capturelog_handler"):
            if call.when == 'teardown':
                root_logger = logging.getLogger()
                root_logger.removeHandler(item.capturelog_handler)

            if not report.passed:
                longrepr = getattr(report, 'longrepr', None)
                if hasattr(longrepr, 'addsection'):
                    log_debug = log_info = ''
                    log_warning = log_error = ''
                    log_critical = ''
                    # @@@ - разделитель логов
                    captured_log = item.capturelog_handler.stream.getvalue()
                    logs_list = captured_log.split('@@@')

                    for lg in logs_list:
                        if '<<DEBUG>>' in lg:
                            log_debug += lg.replace('<<DEBUG>>', '')
                        elif '<<INFO>>' in lg:
                            log_info += lg.replace('<<INFO>>', '')
                        elif '<<WARNING>>' in lg:
                            log_warning += lg.replace('<<WARNING>>', '')
                        elif '<<ERROR>>' in lg:
                            log_error += lg.replace('<<ERROR>>', '')
                        elif '<<CRITICAL>>' in lg:
                            log_critical += lg.replace('<<CRITICAL>>', '')

                    with allure.step(u'[Логи]'):
                        if log_debug:
                            longrepr.addsection(
                                'Логи [debug]', f"\n{log_debug}")
                            allure.attach(log_debug, name='Логи [DEBUG]')
                        if log_info:
                            longrepr.addsection(
                                'Логи [info]', f"\n{log_info}")
                            allure.attach(log_info, name='Логи [INFO]')
                        if log_warning:
                            longrepr.addsection(
                                'Логи [warning]', f"{log_warning}")
                            allure.attach(log_warning, name='Логи [WARNING]')
                        if log_error:
                            longrepr.addsection(
                                'Логи [error]', f"{log_error}")
                            allure.attach(log_error, name='Логи [ERROR]')
                        if log_critical:
                            longrepr.addsection(
                                'Логи [critical]', f"{log_critical}")
                            allure.attach(log_critical, name='Логи [CRITICAL]')

            if call.when == 'teardown':
                item.capturelog_handler.close()
                del item.capturelog_handler

        return report


class LoggerHandler(logging.StreamHandler):

    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.stream = py.io.TextIO()
        self.records = []

    def close(self):
        logging.StreamHandler.close(self)
        self.stream.close()
