import socket
import threading

from WebSocketFrame import WebSocketFrame

HOST = "0.0.0.0"
PORT = 80

def build_fake_handshake():
    """
    Réponse HTTP minimale permettant au client MartyPy
    de considérer la connexion comme 'upgradée'.
    """

    response = (
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Accept: dummy\r\n"
        "\r\n"
    )

    return response.encode()


def handle_client(client_socket, address):

    print(f"[+] Client connecté : {address}")

    # -------------------------------------------------
    # 1) Lecture de la requête HTTP Upgrade
    # -------------------------------------------------

    request = client_socket.recv(4096)

    print("----- HANDSHAKE CLIENT -----")
    print(request.decode(errors="ignore"))

    # -------------------------------------------------
    # 2) Envoi du faux handshake websocket
    # -------------------------------------------------

    client_socket.send(build_fake_handshake())

    print("[+] Upgrade websocket accepté")

    # -------------------------------------------------
    # 3) Boucle principale
    # -------------------------------------------------

    while True:

        try:
            data = client_socket.recv(4096)
            ws = WebSocketFrame()
            if not data:
                break
            
            frame = ws.decode(data)

            print(f"Stats : ", frame.getStats())
            
            reply = ws.encode(
                b"ACK",
                opcode=WebSocketFrame.OPCODE_BINARY,
                useMask=False,
                fin=True
            )

            # Echo simple :
            client_socket.send(reply)

        except Exception as e:
            print("Erreur :", e)
            break

    client_socket.close()
    print("[-] Client déconnecté")


def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen(5)

    print(f"[+] Serveur en écoute sur {HOST}:{PORT}")

    while True:

        client_socket, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(client_socket, addr)
        )

        thread.start()


if __name__ == "__main__":
    start_server()