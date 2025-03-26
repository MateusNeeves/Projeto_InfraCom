import socket
import os
import random

serverPort = 12000
buffer_size = 1024  # Tamanho do buffer
path = "../ReceivedFiles/"

# Criar socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("localhost", serverPort))

# Criar diretório de recebimento se não existir
if not os.path.exists(path):
    os.mkdir(path)
    print(f"Pasta '{path}' criada para armazenar os arquivos recebidos.")

print("Servidor pronto para receber arquivos...")

# Receber nome do arquivo
filename, client_address = server_socket.recvfrom(buffer_size)
filename = filename.decode('utf-8')
print(f"Recebendo arquivo: {filename}")

# Abrir arquivo para escrita
seq_num_expected = 0
with open(path + filename, "wb") as file:
    while True:
        try:
            data, client_address = server_socket.recvfrom(buffer_size)
            if data == b"EOF":
                break

            # Introduzindo erro aleatório no pacote
            if random.random() < 0.2:  # 20% de chance de erro
                print(f"Erro simulado: Pacote perdido!")
                continue  # Ignora o pacote corrompido
            
            # Decodificar os dados e extrair o número de sequência
            header, msg = data.split(b'|',1)  # Decodifica o pacote
            seq_num_received = int(header.decode('utf-8'))  # Extrai o número de sequência dos dois primeiros caracteres
            content = msg  # O restante é o conteúdo do pacote

            if seq_num_received == seq_num_expected:
                file.write(content)  # Escreve o conteúdo no arquivo
                server_socket.sendto(f"ACK{seq_num_expected}".encode('utf-8'), client_address)
                print(f"Pacote {seq_num_received} recebido corretamente.")
                seq_num_expected = 1 - seq_num_expected  # Alterna sequência
            else:
                print(f"Erro de sequência: Esperado {seq_num_expected}, mas recebido {seq_num_received}. Ignorando pacote.")
    
        except ConnectionResetError:
            print("Erro: A conexão foi fechada pelo cliente. Finalizando...")
            break

# Indicar fim da recepção
print(f"Arquivo '{filename}' recebido com sucesso e salvo em {path}")
