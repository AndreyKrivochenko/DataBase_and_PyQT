"""Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
 В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
 («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции
  ip_address()."""
import subprocess
from ipaddress import ip_address


def host_ping(begin_addr: str, end_addr: str):
    addr_count = int(ip_address(end_addr)) - int(ip_address(begin_addr)) + 1
    begin_count = int(begin_addr.split('.')[-1])
    end_count = begin_count + addr_count
    for i in range(begin_count, end_count):
        address = begin_addr.split('.')[:-1]
        address.append(str(i))
        address = '.'.join(address)
        print(f'Адрес {address}\t-\t', end='')
        process = subprocess.run(['ping', '-c', '3', '-q', address], stdout=subprocess.DEVNULL)
        print('Узел недоступен' if process.returncode else 'Узел доступен')


if __name__ == '__main__':
    host_ping('192.168.88.137', '192.168.88.150')
