import socket
import random

buffer_size = 1024

def send(seq_num, data, sender_socket, address):
    n = 0
    m = buffer_size - 2
    while n <= len(data):
        chunk = data[n:m]
        ack_received = False

        if chunk == b"EOF":
            return None  # Indica o fim da transmissão

        packet = f"{seq_num[0]}|" + chunk  # Corrigido
        # print(f"Pacote {seq_num[0]} enviado.")
        sender_socket.sendto(packet.encode('utf-8'), address)
        while not ack_received:
            try:
                ack, _ = sender_socket.recvfrom(buffer_size)
                if ack.decode('utf-8') == f"ACK{seq_num[0]}":
                    ack_received = True
                    # print(f"ACK {seq_num[0]} recebido.")
                    seq_num[0] = 1 - seq_num[0]  # Alterna sequência entre 0 e 1
            except sender_socket.timeout:
                # print(f"Timeout! Reenviando pacote {seq_num[0]}...")
                sender_socket.sendto(packet.encode('utf-8'), address)
            except ConnectionResetError:
                print("Erro: A conexão foi fechada pelo servidor. Tentando reconectar...")
                break

        n = m
        m += buffer_size - 2

def receive(seq_num_expected, data, receiver_socket, address):
    try:
        if data == b"EOF":
            return None  # Indica o fim da transmissão
        
        # if random.random() < 0.1:  # 10% de chance de erro
        #     # print(f"Erro simulado: Pacote perdido!")
        #     return None  # Ignora o pacote perdido

        # Decodificar os dados e extrair o número de sequência
        header, msg = data.split(b'|', 1)  # Decodifica o pacote
        seq_num_received = int(header.decode('utf-8'))  # Extrai o número de sequência
        content = msg  # O restante é o conteúdo do pacote

        if seq_num_received == seq_num_expected[0]:
            receiver_socket.sendto(f"ACK{seq_num_expected[0]}".encode('utf-8'), address)
            # print(f"Pacote {seq_num_received} recebido corretamente.")
            seq_num_expected[0] = 1 - seq_num_expected[0]  # Alterna sequência
            return content  # Retorna a mensagem recebida
        else:
            receiver_socket.sendto(f"ACK{seq_num_received}".encode('utf-8'), address)
            # print(f"Erro de sequência: Esperado {seq_num_expected[0]}, mas recebido {seq_num_received}. Reenviando ACK{seq_num_received}.")
            return None  # Ignora o pacote fora de ordem

    except ConnectionResetError:
        print("Erro: A conexão foi fechada pelo cliente. Finalizando...")
        return None