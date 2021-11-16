"""Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
 В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
 («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции
  ip_address()."""
import subprocess
from ipaddress import ip_address


def host_ping(addr_lst: list):
    for el in addr_lst:
        print(f'Адрес {ip_address(el)}\t-\t', end='')
        process = subprocess.run(['ping', '-c', '3', str(ip_address(el))], stdout=subprocess.DEVNULL)
        print('Узел недоступен' if process.returncode else 'Узел доступен')


if __name__ == '__main__':
    host_ping(['192.168.88.77', '192.168.88.56', '192.168.88.92'])
