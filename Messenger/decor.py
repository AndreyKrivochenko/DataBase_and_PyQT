import sys
import logging
from project_log.config import conf_server_log, conf_client_log
import inspect

if sys.argv[0].find('client') != -1:
    LOGGER = logging.getLogger('client')
else:
    LOGGER = logging.getLogger('server')


class Log:
    def __call__(self, func):
        def save_log(*args, **kwargs):
            result = func(*args, **kwargs)
            LOGGER.debug(f'Вызвана функция {func.__name__} с параметрами {args}, {kwargs}. '
                         f'Вызов из модуля {func.__module__}.'
                         f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
            return result
        return save_log
