import socket
import os

server_path = "C:/Users/Brandon/source/repos/cse-3320-assignment-4/server/Users"

def writeFile(connection, filename, user, data):
    file_path = "%s/%s/%s.encrypt" % (server_path, user, filename)
    f = open(file_path, "wb")
    f.write(data.encode())
    f.close()

def main():
    print("**********SERVER**********")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 2127))
    server_socket.listen(5)
    
    print("Accepted connection and listening...")

    
    while True:
        (connection, address) = server_socket.accept()
        buf = connection.recv(4)
        if buf.decode("UTF-8") == "push":
          input = ""
          while True:
            buf = connection.recv(1000)
            if buf:
                input += buf.decode("UTF-8")
                print("Received Packet")
            else:
                break

          data = input.split("~")
          username = data[0]
          filename = data[1]
          content = data[2]

          user_path = "%s/%s" % (server_path, username)
          if not os.path.exists(user_path):
              os.makedirs(user_path)

          writeFile(connection, filename, username, content)

        if buf.decode("UTF-8") == "pull":
            #get filename
            buf = connection.recv(1000)
            file = open(buf.decode("UTF-8"), "rb")
            connection.sendfile(file)
            connection.send(b"~")
            file.close

    return 0

main()