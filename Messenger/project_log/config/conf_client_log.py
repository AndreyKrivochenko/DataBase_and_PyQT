import logging
from common.variables import LOGGING_LEVEL
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent.joinpath('log', 'client.log')

CLIENT_FORMATTER = logging.Formatter('%(asctime)-27s %(levelname)-12s %(filename)-25s %(message)s')
STREAM_HANDLER = logging.StreamHandler(sys.stdout)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.CRITICAL)

FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
FILE_HANDLER.setFormatter(CLIENT_FORMATTER)

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.info('Информация')
    LOGGER.debug('Отладка')
    LOGGER.error('Ошибка')
