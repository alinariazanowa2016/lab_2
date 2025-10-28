import socket

HOST = '127.0.0.1'
PORT = 65432        
nm
def echo_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"Подключено к {HOST}:{PORT}")
            while True:
                message = input("Введите сообщение (или 'exit' для выхода): ")
                if message.lower() == 'exit':
                    break
                s.sendall(message.encode('utf-8'))
                data = s.recv(1024)
                print(f"Ответ от сервера: {data.decode('utf-8')}")
        except ConnectionRefusedError:
            print("Не удалось подключиться к серверу. Убедитесь, что сервер запущен.")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
    print("Соединение закрыто.")

if __name__ == '__main__':
    echo_client()
