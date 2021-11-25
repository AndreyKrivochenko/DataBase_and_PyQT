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


class Client:
    def __init__(self):
        self.server_address = None
        self.server_port = None
        self.client_name = None
        self.presense = None
        self.server_answer = None
        self.message = None

    @Log()
    def argument_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
        parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
        parser.add_argument('-n', '--name', default=None, nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        self.server_address = namespace.addr
        self.server_port = namespace.port
        self.client_name = namespace.name
        if 1024 > self.server_port > 65535:
            CLIENT_LOGGER.critical(f'Попытка запуска клиента с недопустимым портом сервера: {self.server_port}. Клиент'
                                   f'завершается')
            sys.exit(1)
        if not self.client_name:
            self.client_name = input('Введите имя пользователя: ')
        CLIENT_LOGGER.info(
            f'Клиент запущен с параметрами сервера: адрес - {self.server_address}, порт - {self.server_port}')

    def create_presense(self):
        self.presense = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.client_name
            }
        }
        CLIENT_LOGGER.debug(f'Для пользователя {self.client_name} сформировано сообщение: {PRESENCE}')

    @Log()
    def process_answ(self, message):
        CLIENT_LOGGER.debug(f'Сообщение от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                self.server_answer = '200: Ok'
            else:
                self.server_answer = f'400: {message[ERROR]}'
        raise ValueError

    @Log()
    def message_from_server(self, sock, my_username):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                self.message = get_message(sock)
                if ACTION in self.message and self.message[
                    ACTION] == MESSAGE and SENDER in self.message and DESTINATION in self.message \
                        and MESSAGE_TEXT in self.message and self.message[DESTINATION] == my_username:
                    print(f'\nПолучено сообщение от пользователя {self.message[SENDER]}:\n{self.message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(
                        f'Получено сообщение от пользователя {self.message[SENDER]}:\n{self.message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {self.message}')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Потеряно соединение с сервером.')
                break

    @Log()
    def user_interactive(self, sock, username):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message(sock, username)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                send_message(sock, self.create_exit_message())
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    def create_exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.client_name
        }

    @staticmethod
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

    @staticmethod
    @Log()
    def print_help():
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')


def main():
    client = Client()
    print('Месседжер. Клиентский модуль.')
    client.argument_parser()
    print(f'Ваше имя пользователя - {client.client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((client.server_address, client.server_port))
        client.create_presense()
        send_message(transport, client.presense)
        client.process_answ(get_message(transport))
        print('Установлено соединение с сервером')
        CLIENT_LOGGER.info(f'Принят ответ от сервера: {client.server_answer}')
    except json.JSONDecodeError:
        print('Не удалось декодировать сообщение сервера')
        CLIENT_LOGGER.error(f'Не удалось декодировать полученную JSON-строку')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {client.server_address}:{client.server_port}')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=client.message_from_server, args=(transport, client.client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=client.user_interactive, args=(transport, client.client_name))
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
