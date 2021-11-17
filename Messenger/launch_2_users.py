import subprocess
import time

PROCESSES = []

while True:
    CHOICE = input('Ваше действие (s - запуск сервера и клиентов, x - закрыть все окна, q - выход): ')

    if CHOICE == 'q':
        break
    elif CHOICE == 's':
        PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 server.py', shell=True))
        # Пауза нужна чтобы сервер успел запуститься. Иначе клиенты не подключаются и закрываются
        time.sleep(0.5)
        PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 client.py -n user1', shell=True))
        PROCESSES.append(subprocess.Popen('gnome-terminal -- python3 client.py -n user2', shell=True))
    elif CHOICE == 'x':
        while PROCESSES:
            PROCESS = PROCESSES.pop()
            PROCESS.kill()
