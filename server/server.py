import socket

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 2127))
    server_socket.listen(5)

    while True:
        (client)
    return 0

main()