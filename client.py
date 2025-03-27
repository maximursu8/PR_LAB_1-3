import socket
import threading

HOST = "127.0.0.1"
PORT = 14542

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break
            print("\n[CHAT] " + message + "\n> ", end="")
        except:
            print("[INFO] Conexiunea cu serverul s-a întrerupt.")
            break

def send_messages(client_socket):
    while True:
        message = input("> ")
        if message.lower() == "exit":
            client_socket.close()
            break
        client_socket.send(message.encode("utf-8"))

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print("[EROARE] Nu mă pot conecta la server.")
        return

    print("[INFO] Conectat la server! Poți trimite mesaje. Scrie 'exit' pentru a ieși.")

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=send_messages, args=(client,))
    send_thread.daemon = True
    send_thread.start()

    send_thread.join()

if __name__ == "__main__":
    start_client()

