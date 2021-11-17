import json
import socket
import sys
import threading
import time
import logging
import argparse
from project_log.config import conf_client_log
from decor import Log

from common.utils import send_message, get_message
from common.variables import DEFAULT_IP_ADDRESS, DEFAULT_PORT, ERROR, RESPONSE, USER, ACCOUNT_NAME, ACTION, \
    PRESENCE, TIME, MESSAGE, SENDER, MESSAGE_TEXT, DESTINATION, EXIT

CLIENT_LOGGER = logging.getLogger('client')


@Log()
def create_exit_message(account_name):
    """Функция создаёт словарь с сообщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@Log()
def message_from_server(sock, my_username):
    """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                print(f'\nПолучено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
            break


@Log()
def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@Log()
def create_message(sock, account_name='Guest'):
    """
    Функция запрашивает кому отправить сообщение и само сообщение,
    и отправляет полученные данные на сервер
    """
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to_user}')
    except Exception:
        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
        sys.exit(1)


@Log()
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


@Log()
def create_presense(account_name):
    result = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Для пользователя {account_name} сформировано сообщение: {PRESENCE}')
    return result


@Log()
def process_answ(message):
    CLIENT_LOGGER.debug(f'Сообщение от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200: Ok'
        return f'400: {message[ERROR]}'
    raise ValueError


@Log()
def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name
    if 1024 > server_port > 65535:
        CLIENT_LOGGER.critical(f'Попытка запуска клиента с недопустимым портом сервера: {server_port}. Клиент'
                               f'завершается')
        sys.exit(1)
    return server_address, server_port, client_name


def main():
    print('Месседжер. Клиентский модуль.')
    server_address, server_port, client_name = argument_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    CLIENT_LOGGER.info(f'Клиент запущен с параметрами сервера: адрес - {server_address}, порт - {server_port}')
    print(f'Ваше имя пользователя - {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presense(client_name)
        send_message(transport, message_to_server)
        answer = process_answ(get_message(transport))
        print('Установлено соединение с сервером')
        CLIENT_LOGGER.info(f'Принят ответ от сервера: {answer}')
    except json.JSONDecodeError:
        print('Не удалось декодировать сообщение сервера')
        CLIENT_LOGGER.error(f'Не удалось декодировать полученную JSON-строку')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()

        CLIENT_LOGGER.debug('Запущены процессы приема и передачи сообщений')
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
