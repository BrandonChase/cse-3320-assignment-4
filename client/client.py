from tkinter.filedialog import askopenfilename
import socket
import os
from cryptography.fernet import Fernet

client_path = "C:/Users/Brandon/source/repos/cse-3320-assignment-4/client/Users"
server_path = "C:/Users/Brandon/source/repos/cse-3320-assignment-4/server/Users"


def sign_in():
    #Get Credentials
    username = input("Enter username (if new will create new account): ")
    password = input("Enter password (if new will set password): ")

    user_path = "%s/%s" % (client_path, username)
    #New User
    if not os.path.exists(user_path):
        #Setup folders
        os.makedirs(user_path)
        os.makedirs(user_path+"/Data")

        #Save password
        password_file = open(user_path + "/password", "w")
        password_file.write(password)
        password_file.close()

        #Save encrypt/decrypt key
        key = Fernet.generate_key()
        key_file = open(user_path + "/key", "w")
        key_file.write(key.decode("UTF-8"))
        key_file.close()

    #Existing User
    else:
        password_file = open(user_path + "/password", "r")
        actual_password = password_file.read()
        password_file.close()
        if password != actual_password:
            print("You entered the wrong password! Try Again.")
            sign_in()

    return username

def get_key(user_path):
    file = open(user_path + "/key", "rb")
    key = file.read()
    file.close()
    return key

def parse_filename(filename):
    data = filename.split("/")
    return data[len(data)-1]

def main():
    print("**********CLIENT**********")

    username = sign_in()
    user_path = "%s/%s" % (client_path, username)
    cipher_suite = Fernet(get_key(user_path))

    while True:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client_socket.connect(("localhost", 2127))

        command = input("[push]/[pull]/[quit]: ")
        #if push, open file explorer, get file, encrypt, send to server
        if command.lower() == "push":
            #Get file content
            filename = askopenfilename(initialdir = user_path+"/Data")
            file = open(filename, "rb")
            content = file.read()
            file.close()

            #Send alert to server and filename
            client_socket.send(b"push")

            #Send user and filename
            parsed_filename = parse_filename(filename)
            client_socket.send(username.encode())
            client_socket.send(b"~")
            client_socket.send(parsed_filename.encode())
            client_socket.send(b"~")

            #Encrypt content and save to temp file
            file = open(filename + ".encrypt", "wb")
            file.write(cipher_suite.encrypt(content))
            file.close()

            #Send temp file to server
            file = open(filename + ".encrypt", "rb")
            client_socket.sendfile(file)
            client_socket.close()
            file.close()

            #Delete temp file
            os.remove(filename + ".encrypt")

        #if pull, send command to server, receive file, decrypt
        if command.lower() == "pull":
            filename = askopenfilename(initialdir = server_path+"/"+username)
            #Send alert to server and filename
            client_socket.send(b"pull")
            #Send filename
            client_socket.send(filename.encode())
            #Receive data
            content = ""
            while True:
                buf = client_socket.recv(1000)
                if buf:
                    content += buf.decode("UTF-8")
                    print("Received Packet")
                if "~" in buf.decode("UTF-8"):
                    content = content[:-1]
                    break

            file = open(user_path+"/Data/" + parse_filename(filename) + ".decrypt", "wb")
            decoded = content.encode()
            data = cipher_suite.decrypt(content.encode())
            file.write(data)
            file.close()

            client_socket.close()

        if command.lower() == "quit":
            break
        
    return 0

main()