import socket
import threading
import sys

SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345
clients = {}


def handle_messages(server_socket):
    """Gestionează mesajele primite de la clienți"""
    while True:
        try:
            data, addr = server_socket.recvfrom(1024)
            message = data.decode()

            if message.startswith("/join"):
                username = message.split(" ", 1)[1]
                if username in clients:
                    server_socket.sendto(
                        "[Eroare] Acest nume este deja folosit.".encode(), addr
                    )
                else:
                    clients[username] = addr
                    print(f"{username} s-a alăturat chat-ului.")
                    server_socket.sendto(
                        "[Chat] V-ați conectat cu succes!".encode(), addr
                    )

                    for user, user_addr in clients.items():
                        if user_addr != addr:
                            server_socket.sendto(
                                f"[Chat] {username} s-a alăturat!".encode(), user_addr
                            )

            elif message == "/users":
                user_list = "Utilizatori activi: " + ", ".join(clients.keys())
                server_socket.sendto(user_list.encode(), addr)

            elif message.startswith("/msg"):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    server_socket.sendto(
                        "[Eroare] Format incorect! Folosiți: /msg <utilizator> <text>".encode(),
                        addr,
                    )
                    continue
                _, recipient, text = parts

                if recipient in clients:
                    sender = [
                        user for user, address in clients.items() if address == addr
                    ][0]
                    server_socket.sendto(
                        f"[Privat] {sender}: {text}".encode(), clients[recipient]
                    )
                else:
                    server_socket.sendto(
                        "[Eroare] Utilizator inexistent!".encode(), addr
                    )

            elif message.startswith("/send"):
                text = message.split(" ", 1)[1]
                sender = [user for user, address in clients.items() if address == addr][
                    0
                ]

                for user, user_addr in clients.items():
                    if user_addr != addr:
                        server_socket.sendto(
                            f"[General] {sender}: {text}".encode(), user_addr
                        )

            elif message.startswith("/exit"):
                username = message.split(" ", 1)[1]
                if username in clients:
                    del clients[username]
                    print(f"{username} s-a deconectat.")
                    for user_addr in clients.values():
                        server_socket.sendto(
                            f"[Chat] {username} s-a deconectat.".encode(), user_addr
                        )

        except Exception as e:
            print(f"Eroare server: {e}")


def start_server():
    """Inițializează serverul"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Serverul rulează pe {SERVER_IP}:{SERVER_PORT}")

    threading.Thread(target=handle_messages, args=(server_socket,), daemon=True).start()

    while True:
        pass


def receive_messages(client_socket):
    """Thread pentru a primi mesaje de la server"""
    while True:
        try:
            data, _ = client_socket.recvfrom(1024)
            message = data.decode()

            if message.startswith("[Eroare]"):
                print(f"\033[91m{message}\033[0m")
            elif message.startswith("[Privat]"):
                print(f"\033[94m{message}\033[0m")
            else:
                print(message)

        except:
            continue


def start_client():
    """Inițializează clientul"""
    server_ip = input("Introduceți IP-ul serverului: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    username = input("Introduceți numele de utilizator: ")
    client_socket.sendto(f"/join {username}".encode(), (server_ip, SERVER_PORT))

    threading.Thread(
        target=receive_messages, args=(client_socket,), daemon=True
    ).start()

    while True:
        msg = input()
        if msg.startswith("/msg"):
            parts = msg.split(" ", 2)
            if len(parts) < 3:
                print(
                    "\033[91m[Eroare] Format incorect! Folosiți: /msg <utilizator> <text>\033[0m"
                )
                continue

            _, recipient, text = parts
            client_socket.sendto(
                f"/msg {recipient} {text}".encode(), (server_ip, SERVER_PORT)
            )
            print(f"\033[94m[Privat] Către {recipient}: {text}\033[0m")

        elif msg.startswith("/send"):
            parts = msg.split(" ", 1)
            if len(parts) < 2:
                print("\033[91m[Eroare] Folosiți: /send <mesaj>\033[0m")
                continue

            _, text = parts
            client_socket.sendto(f"/send {text}".encode(), (server_ip, SERVER_PORT))
            print(f"\033[92m[General] Tu: {text}\033[0m")

        elif msg == "/users":
            client_socket.sendto("/users".encode(), (server_ip, SERVER_PORT))

        elif msg == "/exit":
            client_socket.sendto(f"/exit {username}".encode(), (server_ip, SERVER_PORT))
            print("\033[93m[Chat] V-ați deconectat!\033[0m")
            client_socket.close()
            sys.exit()

        else:
            print(
                "\033[91m[Eroare] Comandă necunoscută! Folosiți /msg, /send, /users, /exit\033[0m"
            )


if __name__ == "__main__":
    mode = input("Rulați ca server (s) sau client (c)? ").strip().lower()

    if mode == "s":
        start_server()
    elif mode == "c":
        start_client()
    else:
        print(
            "Opțiune invalidă! Rulați din nou și alegeți 's' pentru server sau 'c' pentru client."
        )
