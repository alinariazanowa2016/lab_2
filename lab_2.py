Задание 1. Простой TCP эхо-сервер и клиент.

TCP Эхо-сервер:
import socket

HOST = '127.0.0.1’ # Стандартный адрес интерфейса обратной связи (localhost)
PORT = 65432        # Порт для прослушивания (непривилегированные порты> 1023)

def echo_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP Echo Server запущен на {HOST}:{PORT}")
        conn, addr = s.accept() # Блокируется до тех пор, пока клиент не подключится
        with conn:
            print(f"Подключено клиентом: {addr}")
            while True:
                try:
                    data = conn.recv(1024) # Принимает до 1024 байт
                    if not data: # Если данных нет, клиент отключился
                        break
                    print(f"Получено от {addr}: {data.decode('utf-8')}")
                    conn.sendall(data) # Отправляем данные обратно клиенту
                    print(f"Отправлено обратно клиенту: {data.decode('utf-8')}")
                except ConnectionResetError:
                    print(f"Клиент {addr} принудительно разорвал существующее соединение.")
                    break
                except Exception as e:
                    print(f"Ошибка при работе с клиентом {addr}: {e}")
                    break
    print("Соединение закрыто.")

if __name__ == '__main__':
    echo_server()

TCP Эхо-клиент:

import socket

HOST = '127.0.0.1'  # IP адрес сервера
PORT = 65432        # Порт, который слушает сервер

def echo_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к серверу {HOST}:{PORT}")
            while True:
                message = input("Введите сообщение для сервера (или 'exit' для выхода): ")
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
                data = s.recv(1024)
                print(f"Получено от сервера: {data.decode('utf-8')}")
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")
if __name__ == '__main__':
    echo_client()
Простой HTTP-сервер на сокетах:
Этот код можно использовать в каждом задании как отдельный модуль или функцию, демонстрирующую реализацию HTTP-сервера.

import socket

HOST_HTTP = '127.0.0.1'
PORT_HTTP = 8080

html_response = b"""\
HTTP/1.1 200 OK\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 70\r\n
\r\n
<html><head><title>Test</title></head><body><h1>Hello, HTTP!</h1></body></html>
"""

http_404_response = b"""\
HTTP/1.1 404 Not Found\r\n
Content-Type: text/html; charset=utf-8\r\n
Content-Length: 58\r\n
\r\n
<html><head><title>404</title></head><body><h1>Not Found</h1></body></html>
"""

def simple_http_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST_HTTP, PORT_HTTP))
        s.listen(1)
        print(f"HTTP Server запущен на http://{HOST_HTTP}:{PORT_HTTP}/")
        while True:
            conn, addr = s.accept()
            with conn:
                print(f"HTTP-запрос от {addr}")
                try:
                    request = conn.recv(1024).decode('utf-8')
                    if not request:
                        continue
                    print(f"Запрос:\n{request}")

                    if request.startswith('GET / HTTP/1.1') or request.startswith('GET / HTTP/1.0'):
                        conn.sendall(html_response)
                    else:
                        conn.sendall(http_404_response)
                except Exception as e:
                    print(f"Ошибка обработки HTTP-запроса от {addr}: {e}")
                finally:
                    conn.close() # Безопасное закрытие соединения

if __name__ == '__main__':
    simple_http_server()

Задание 2. Многопользовательский TCP чат.

Многопользовательский TCP Чат-сервер:

import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

# Список для хранения всех активных клиентских соединений
clients = []
clients_lock = threading.Lock() # Мьютекс для безопасного доступа к списку клиентов

def handle_client(conn, addr):
    print(f"Новое подключение: {addr}")
    with clients_lock:
        clients.append(conn)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"Получено от {addr}: {message}")
            
            # Рассылаем сообщение всем остальным клиентам
            with clients_lock:
                for client_socket in clients:
                    if client_socket != conn: # Не отправляем сообщение отправителю
                        try:
                            client_socket.sendall(f"От {addr}: {message}".encode('utf-8'))
                        except:
                            # Удаляем неработающий сокет
                            clients.remove(client_socket)
                            print(f"Удален неработающий сокет клиента.")
    except ConnectionResetError:
        print(f"Клиент {addr} принудительно разорвал соединение.")
    except Exception as e:
        print(f"Ошибка при работе с клиентом {addr}: {e}")
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"Клиент {addr} отключился.")

def chat_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Чат-сервер запущен на {HOST}:{PORT}")
        while True:
            try:
                conn, addr = s.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True # Позволяет основной программе завершиться, даже если потоки активны
                thread.start()
            except KeyboardInterrupt:
                print("Сервер остановлен пользователем.")
                break
            except Exception as e:
                print(f"Ошибка принятия соединения: {e}")
    print("Сервер завершил работу.")

if __name__ == '__main__':
    # Запускаем HTTP-сервер в отдельном потоке, чтобы он работал параллельно
    # http_thread = threading.Thread(target=simple_http_server)
    # http_thread.daemon = True
    # http_thread.start()

    chat_server()

TCP Чат-клиент:

import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(f"\n{data.decode('utf-8')}")
        except ConnectionResetError:
            print("Соединение с сервером разорвано.")
            break
        except Exception as e:
            print(f"Ошибка приема: {e}")
            break
    print("Прием сообщений остановлен.")
    sys.exit() # Закрываем клиент после разрыва соединения

def chat_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к чат-серверу {HOST}:{PORT}")

            # Запускаем поток для приема сообщений
            receive_thread = threading.Thread(target=receive_messages, args=(s,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                message = input("") # Пустой input, чтобы не мешать выводу сообщений
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")

if __name__ == '__main__':
    chat_client()

Задание 3. UDP передача сообщений.

UDP Эхо-сервер:

import socket

HOST = '127.0.0.1'
PORT = 65432

def udp_echo_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        print(f"UDP Echo Server запущен на {HOST}:{PORT}")
        while True:
            try:
                data, addr = s.recvfrom(1024) # Принимаем данные и адрес отправителя
                message = data.decode('utf-8')
                print(f"Получено от {addr}: {message}")
                s.sendto(data, addr) # Отправляем данные обратно отправителю
                print(f"Отправлено обратно {addr}: {message}")
            except Exception as e:
                print(f"Ошибка UDP сервера: {e}")
                break

if __name__ == '__main__':
    udp_echo_server()

UDP Эхо-клиент:

import socket

HOST = '127.0.0.1'
PORT = 65432
SERVER_ADDR = (HOST, PORT)

def udp_echo_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        print(f"UDP Echo Client запущен. Целевой сервер: {HOST}:{PORT}")
        while True:
            message = input("Введите сообщение для сервера (или 'exit' для выхода): ")
            if message.lower() == 'exit':
                break
            try:
                s.sendto(message.encode('utf-8'), SERVER_ADDR)
                s.settimeout(1.0) # Устанавливаем таймаут для приема ответа
                data, addr = s.recvfrom(1024)
                print(f"Получено от сервера {addr}: {data.decode('utf-8')}")
            except socket.timeout:
                print("Таймаут: Сервер не ответил.")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                break
    print("Соединение закрыто.")

if __name__ == '__main__':
    udp_echo_client()

