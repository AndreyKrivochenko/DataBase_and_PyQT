import logging

# Уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Основные сетевые переменные
DEFAULT_PORT = 8899
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTION = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

# JIM Ключи
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
DESTINATION = 'to'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'

# Словари - ответы:
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
