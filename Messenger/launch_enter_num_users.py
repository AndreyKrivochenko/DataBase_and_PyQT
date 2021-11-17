import subprocess
import time

PROCESSES = []

while True:
    CHOICE = input('Ваше действие (s - запуск сервера и клиентов, x - закрыть все окна, q - выход): ')

    if CHOICE == 'q':
        break
    elif CHOICE == 's':
        num = int(input('Введите количество клиентов: '))
        PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))
        # Пауза нужна чтобы сервер успел запуститься. Иначе клиенты не подключаются и закрываются
        time.sleep(0.5)
        for i in range(1, num + 1):
            PROCESSES.append(subprocess.Popen(f'gnome-terminal -- python3 client.py -n user{i}', shell=True))
    elif CHOICE == 'x':
        while PROCESSES:
            PROCESS = PROCESSES.pop()
            PROCESS.kill()
