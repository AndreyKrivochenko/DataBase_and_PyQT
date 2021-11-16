"""Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона. Меняться должен только последний
 октет каждого адреса. По результатам проверки должно выводиться соответствующее сообщение."""
import subprocess
from ipaddress import ip_address


def host_range_ping(begin_addr: str, end_addr: str):
    begin_addr = int(ip_address(begin_addr))
    end_addr = int(ip_address(end_addr))
    for i in range(begin_addr, end_addr + 1):
        print(f'Адрес {ip_address(i)}\t-\t', end='')
        process = subprocess.run(['ping', '-c', '3', str(ip_address(i))], stdout=subprocess.DEVNULL)
        print('Узел недоступен' if process.returncode else 'Узел доступен')


if __name__ == '__main__':
    host_range_ping('192.168.88.1', '192.168.88.10')
