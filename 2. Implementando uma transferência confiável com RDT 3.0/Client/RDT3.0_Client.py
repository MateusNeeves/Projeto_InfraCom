import socket
import os
import random
import time

serverName = "localhost"
serverPort = 12000
buffer_size = 1024  # Tamanho do buffer
path = "../Files/"

print("Digite o nome do arquivo:")
for file in os.listdir(path):
    print("- " + file)
filename = input()

# Criar socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1)  # Timeout para retransmissão

# Enviar nome do arquivo
client_socket.sendto(filename.encode('utf-8'), (serverName, serverPort))
print(f"Arquivo {filename} enviado para o servidor.")

# Envio dos pacotes com Stop-and-Wait ARQ
seq_num = 0

with open(path + filename, "rb") as file:
    chunk = file.read(buffer_size - 2)  # Subtrair 2 bytes para o número de sequência
    while chunk:
        ack_received = False
        packet = f"{seq_num}|".encode('utf-8') + chunk  # Adiciona o número de sequência ao pacote
        client_socket.sendto(packet, (serverName, serverPort))
        print(f"Pacote {seq_num} enviado.")
        while not ack_received:
            try:
                ack, _ = client_socket.recvfrom(buffer_size)
                if ack.decode('utf-8') == f"ACK{seq_num}":
                    ack_received = True
                    print(f"ACK {seq_num} recebido.")
                    seq_num = 1 - seq_num  # Alterna sequência entre 0 e 1
            except socket.timeout:
                client_socket.sendto(packet, (serverName, serverPort))
                print(f"Timeout! Reenviando pacote {seq_num}...")
            except ConnectionResetError:
                print("Erro: A conexão foi fechada pelo servidor. Tentando reconectar...")
                break  # Ou você pode tentar reconectar aqui

        chunk = file.read(buffer_size - 2)  # Continua lendo o arquivo

# Indicar fim da transmissão
client_socket.sendto(b"EOF", (serverName, serverPort))
print("Fim da transmissão do arquivo.")

print("Arquivo enviado com sucesso!")
