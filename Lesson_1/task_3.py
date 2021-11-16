"""Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2. Но в данном случае
 результат должен быть итоговым по всем ip-адресам, представленным в табличном формате (использовать модуль tabulate).
  """
import subprocess
from ipaddress import ip_address
from tabulate import tabulate


def host_range_ping(begin_addr: str, end_addr: str):
    begin_addr = int(ip_address(begin_addr))
    end_addr = int(ip_address(end_addr))
    table = {
        'Reachable': [],
        'Unreachable': []
    }
    for i in range(begin_addr, end_addr + 1):
        address = str(ip_address(i))
        process = subprocess.run(['ping', '-c', '2', address], stdout=subprocess.DEVNULL)
        if process.returncode:
            table['Unreachable'].append(address)
        else:
            table['Reachable'].append(address)
    print(tabulate(table, headers='keys', tablefmt='presto'))


if __name__ == '__main__':
    host_range_ping('192.168.88.1', '192.168.88.10')
