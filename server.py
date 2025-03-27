import socket
import threading
import signal

HOST = "0.0.0.0"
PORT = 14542

clients = []
clients_lock = threading.Lock()
running = True

def broadcast(message):
    with clients_lock:
        for client in clients[:]:
            try:
                client.send(message)
            except:
                clients.remove(client)

def handle_client(client_socket, addr):
    print(f"[INFO] Client conectat: {addr}")
    
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            print(f"[{addr}] {message.decode('utf-8')}")
            broadcast(message)
        except:
            break

    print(f"[INFO] Client deconectat: {addr}")
    with clients_lock:
        if client_socket in clients:
            clients.remove(client_socket)
    client_socket.close()

def signal_handler(sig, frame):
    global running
    print("\n[INFO] Se închide serverul...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    server.settimeout(1.0)
    print(f"[INFO] Serverul rulează pe {HOST}:{PORT}")

    while running:
        try:
            client_socket, addr = server.accept()
            with clients_lock:
                clients.append(client_socket)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
        except socket.timeout:
            continue

    print("[INFO] Serverul s-a oprit.")
    server.close()

if __name__ == "__main__":
    start_server()

