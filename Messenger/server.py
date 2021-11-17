import argparse
import json
import socket
import sys
import logging
import select
import time

from project_log.config import conf_server_log
from decor import Log

from common.utils import send_message, get_message
from common.variables import DEFAULT_PORT, MAX_CONNECTION, ACTION, ACCOUNT_NAME, RESPONSE, PRESENCE, TIME,\
    USER, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT, RESPONSE_200, RESPONSE_400


SERVER_LOGGER = logging.getLogger('server')


@Log()
def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, отправляет словарь-ответ в случае необходимости.
    """
    SERVER_LOGGER.debug(f'Сообщение от клиента: {message}')
    if ACTION in message and message[ACTION] == PRESENCE and USER in message and TIME in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя занято'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and MESSAGE_TEXT in message and DESTINATION in message and SENDER in message:
        messages_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Некорректный запрос'
        send_message(client, response)
        return


@Log()
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} от пользователя'
                           f' {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, отправка'
                            f' сообщения невозможна.')


@Log()
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Попытка запуска сервера с неподходящим номером порта: {listen_port}')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()

    SERVER_LOGGER.info(f'Сервер запущен. Адрес - {listen_address}, порт - {listen_port}')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.1)

    client_list = []
    message_list = []
    names = dict()

    transport.listen(MAX_CONNECTION)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            SERVER_LOGGER.info(f'Установлено соединение с клиентом: {client_address}')
            client_list.append(client)

        receive_data_list = []
        send_data_list = []
        error_data_list = []

        try:
            receive_data_list, send_data_list, error_data_list = select.select(client_list, client_list, [], 0)
        except OSError:
            pass

        if receive_data_list:
            for client_with_message in receive_data_list:
                try:
                    process_client_message(get_message(client_with_message), message_list, client_with_message,
                                           client_list, names)
                except Exception:
                    SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()} отключился от сервера')
                    client_list.remove(client_with_message)

        for mess in message_list:
            try:
                process_message(mess, names, send_data_list)
            except Exception:
                SERVER_LOGGER.info(f'Связь с клиентом с именем {mess[DESTINATION]} была потеряна')
                client_list.remove(names[mess[DESTINATION]])
                del names[mess[DESTINATION]]
            message_list.clear()


if __name__ == '__main__':
    main()
