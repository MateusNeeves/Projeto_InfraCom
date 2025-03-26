import socket
import os
import random
from threading import Thread

serverPort = 12000
buffer_size = 1024  # Tamanho do buffer
clientList = {}
onlineClients = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("localhost", serverPort))

print("Servidor pronto para receber arquivos...")

while True:
    data, client_address = server_socket.recvfrom(buffer_size)
    # Thread(target=, args=(data, target_address)).start()