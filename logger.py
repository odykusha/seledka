
import py
import logging

import allure

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                              Logger Configure
# --------------------------------------------------------------------------- #
class LoggerFilter(logging.Filter):

    def filter(self, record):
        return record.levelno > 10


class Logger(object):

    def pytest_runtest_setup(self, item):
        # @@@ - разделитель логов
        item.capturelog_handler = LoggerHandler()
        item.capturelog_handler.setFormatter(logging.Formatter(
            "<<%(levelname)s>>%(asctime)s.%(msecs)03d\t%(message)s@@@",
            "%H:%M:%S"
        ))
        root_logger = logging.getLogger()

        item.capturelog_handler.addFilter(LoggerFilter())
        root_logger.addHandler(item.capturelog_handler)
        root_logger.setLevel(logging.NOTSET)

    def pytest_runtest_makereport(self, __multicall__, item, call):

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
                    log_critical = log_exception = ''
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
                        elif '<<EXCEPTION>>' in lg:
                            log_exception += lg.replace('<<EXCEPTION>>', '')

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
                        if log_exception:
                            longrepr.addsection(
                                'Логи [exception]', f"{log_exception}")
                            allure.attach(log_exception,
                                          name='Логи [EXCEPTION]')

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
