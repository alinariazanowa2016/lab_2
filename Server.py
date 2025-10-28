import socket

HOST = '127.0.0.1'
PORT = 65432       

def echo_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP Echo Server запущен на {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            print(f"Подключение от {addr}")
            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f"Получено: {data.decode('utf-8')}")
                    conn.sendall(data)
                    print(f"Отправлено обратно: {data.decode('utf-8')}")
                except ConnectionResetError:
                    print(f"Соединение с {addr} сброшено клиентом.")
                    break
                except Exception as e:
                    print(f"Ошибка: {e}")
                    break
    print("Соединение закрыто.")

if __name__ == '__main__':
    echo_server()

