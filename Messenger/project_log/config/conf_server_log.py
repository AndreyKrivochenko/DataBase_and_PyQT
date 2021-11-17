import logging
import logging.handlers
from common.variables import LOGGING_LEVEL
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent.joinpath('log', 'server.log')

SERVER_FORMATTER = logging.Formatter('%(asctime)-27s %(levelname)-12s %(filename)-25s %(message)s')

STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.INFO)

FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf-8', interval=1, when='D')
FILE_HANDLER.setFormatter(SERVER_FORMATTER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.info('Информация')
    LOGGER.debug('Отладка')
    LOGGER.error('Ошибка')