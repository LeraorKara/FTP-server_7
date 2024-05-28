import os
import socket
import logging
import threading

WORKING_DIRECTORY = 'work_dir'
USERS_FILE = 'users.txt'

logging.basicConfig(filename='server.log', level=logging.DEBUG, encoding='utf8')


def load_users():
    users = {}
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            for line in f:
                username, password = line.strip().split()
                users[username] = password
    return users


def save_user(username, password):
    with open(USERS_FILE, 'a') as f:
        f.write(f'{username} {password}\n')


def process(request):
    try:
        parts = request.split()
        if len(parts) == 0:
            return 'неправильный запрос'

        cmd = parts[0]

        if cmd == 'pwd':
            return os.getcwd()

        elif cmd == 'ls':
            if not os.listdir():
                return 'папка пуста'
            return ' '.join(os.listdir())

        elif cmd == 'mkdir':
            if len(parts) < 2:
                return 'неправильный запрос'
            dir_name = parts[1]
            os.mkdir(dir_name)
            return f'Папка {dir_name} создана'

        elif cmd == 'rmdir':
            if len(parts) < 2:
                return 'неправильный запрос'
            dir_name = parts[1]
            os.rmdir(dir_name)
            return f'Папка {dir_name} удалена'

        elif cmd == 'rm':
            if len(parts) < 2:
                return 'неправильный запрос'
            file_name = parts[1]
            os.remove(file_name)
            return f'Файл {file_name} удален'

        elif cmd == 'rename':
            if len(parts) < 3:
                return 'неправильный запрос'
            old_name = parts[1]
            new_name = parts[2]
            os.rename(old_name, new_name)
            return f'Файл {old_name} переименован в {new_name}'

        elif cmd == 'upload':
            if len(parts) < 3:
                return 'неправильный запрос'
            file_name = parts[1]
            file_content = ' '.join(parts[2:])

            with open(file_name, 'w') as f:
                f.write(file_content)
            return f'Файл {file_name} загружен'

        elif cmd == 'download':
            if len(parts) < 2:
                return 'неправильный запрос'
            file_name = parts[1]
            if not os.path.exists(file_name):
                return f'Файл {file_name} не существует'
            with open(file_name, 'r') as f:
                return f.read()

        else:
            return 'неправильный запрос'

    except Exception as e:
        return str(e)


def handle_client(conn, addr, users):
    logging.info(f"Подключение от {addr}")
    conn.send("Введите логин: ".encode())
    username = conn.recv(1024).decode().strip()
    conn.send("Введите пароль: ".encode())
    password = conn.recv(1024).decode().strip()

    if not os.path.exists(WORKING_DIRECTORY):
        os.mkdir(WORKING_DIRECTORY)
    os.chdir(WORKING_DIRECTORY)

    if username in users and users[username] == password:
        conn.send("Добро пожаловать!\n".encode())
    elif username not in users:
        users[username] = password
        save_user(username, password)
        os.mkdir(username)
        conn.send("Регистрация прошла успешно!\n".encode())
    else:
        conn.send("Неверный логин или пароль.\n".encode())
        conn.close()
        return

    if os.curdir != username:
        os.chdir(username)

    while True:
        request = conn.recv(1024).decode()
        if not request or request == 'exit':
            conn.close()
            break
        response = process(request)
        conn.send(response.encode())


if __name__ == '__main__':
    HOST = input('HOST (default "localhost"): ')
    HOST = 'localhost' if not HOST else HOST
    PORT = input('PORT (default 8000): ')
    PORT = int(PORT) if PORT else 8000

    users = load_users()

    sock = socket.socket()
    sock.bind((HOST, PORT))
    sock.listen()

    while True:
        print("Слушаем порт", PORT)
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr, users)).start()
