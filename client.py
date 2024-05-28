import logging
import socket

logging.basicConfig(filename='client.log', level=logging.DEBUG, encoding='utf8')

if __name__ == '__main__':
    HOST = input('HOST (default "localhost"): ')
    HOST = 'localhost' if not HOST else HOST
    PORT = input('PORT (default 8000): ')
    PORT = int(PORT) if PORT else 8000
    sock = socket.socket()
    sock.connect((HOST, PORT))

    response = sock.recv(1024).decode()
    print(response)
    username = input()
    sock.send(username.encode())

    response = sock.recv(1024).decode()
    print(response)
    password = input()
    sock.send(password.encode())

    response = sock.recv(1024).decode()
    print(response)
    if "Неверный логин или пароль" in response:
        sock.close()
    else:
        while True:
            request = input('Write command - ')
            if request == 'exit':
                sock.close()
                break
            sock.send(request.encode())
            response = sock.recv(1024).decode()
            logging.info(response)
            print(response)
