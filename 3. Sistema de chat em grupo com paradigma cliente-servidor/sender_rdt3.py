import socket
import os
import random
import time

def send(data, port):
    serverName = "localhost"
    serverPort = port
    buffer_size = 1024  # Tamanho do buffer

    # Criar socket UDP
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_socket.settimeout(1)  # Timeout para retransmissão

    # Envio dos pacotes com Stop-and-Wait ARQ
    seq_num = 0

    chunk = data.read(buffer_size - 2)  # Subtrair 2 bytes para o número de sequência
    n = 0
    m = buffer_size - 2
    while n <= len(data):
        chunk = data[n:m]
        ack_received = False
        packet = f"{seq_num}|".encode('utf-8') + chunk  # Adiciona o número de sequência ao pacote
        sender_socket.sendto(packet, (serverName, serverPort))
        print(f"Pacote {seq_num} enviado.")
        while not ack_received:
            try:
                ack, _ = sender_socket.recvfrom(buffer_size)
                if ack.decode('utf-8') == f"ACK{seq_num}":
                    ack_received = True
                    print(f"ACK {seq_num} recebido.")
                    seq_num = 1 - seq_num  # Alterna sequência entre 0 e 1
            except socket.timeout:
                sender_socket.sendto(packet, (serverName, serverPort))
                print(f"Timeout! Reenviando pacote {seq_num}...")
            except ConnectionResetError:
                print("Erro: A conexão foi fechada pelo servidor. Tentando reconectar...")
                break  # Ou você pode tentar reconectar aqui

        n = m
        m += buffer_size - 2

    # Indicar fim da transmissão
    sender_socket.sendto(b"EOF", (serverName, serverPort))

