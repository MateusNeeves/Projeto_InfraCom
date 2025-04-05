buffer_size = 1024  # Tamanho máximo de cada pacote (menos alguns bytes de overhead)

def send(seq_num, data, sender_socket, address):
    """
    Função responsável por enviar dados usando um protocolo confiável.
    O parâmetro seq_num é uma lista (para ser alterado por referencia) que mantém o número de sequência atual.
    data é a mensagem (string) a ser enviada.
    sender_socket é o socket que envia o pacote.
    address é o endereço (IP, porta) do destinatário.
    """
    n = 0
    # Define o tamanho do chunk para cada envio (subtrai 2 para acomodar cabeçalho da sequência)
    m = buffer_size - 2
    
    # Envia a mensagem em pedaços até cobrir todo o seu comprimento
    while n <= len(data):
        # Separa o trecho atual da mensagem
        chunk = data[n:m]
        ack_received = False

        # Checa se esta parte do chunk é "EOF" (fim de arquivo)
        if chunk == b"EOF":
            return None  # Indica o fim da transmissão

        # Monta o pacote junto com o número de sequência no cabeçalho
        packet = f"{seq_num[0]}|" + chunk
        # Envia o pacote (convertendo para bytes UTF-8)
        sender_socket.sendto(packet.encode('utf-8'), address)

        # Aguarda o ACK correspondente
        while not ack_received:
            try:
                ack, _ = sender_socket.recvfrom(buffer_size)
                # Se o ACK recebido corresponde ao número de sequência atual
                if ack.decode('utf-8') == f"ACK{seq_num[0]}":
                    ack_received = True
                    # Alterna o número de sequência entre 0 e 1
                    seq_num[0] = 1 - seq_num[0]
            except sender_socket.timeout:
                # Em caso de timeout, reenvia o pacote
                sender_socket.sendto(packet.encode('utf-8'), address)
            except ConnectionResetError:
                # Se a conexão for resetada, exibe mensagem e tenta reconectar
                print("Erro: A conexão foi fechada pelo servidor. Tentando reconectar...")
                break

        # Atualiza os marcadores para enviar o próximo chunk
        n = m
        m += buffer_size - 2

def receive(seq_num_expected, data, receiver_socket, address):
    """
    Função responsável por receber dados de forma confiável.
    seq_num_expected é uma lista que mantém o número de sequência esperado.
    data é o pacote recebido (em bytes).
    receiver_socket é o socket que recebe o pacote.
    address é o endereço do remetente (IP, porta).
    """
    try:
        # Se chegou um pacote marcando "EOF", indica fim da transmissão
        if data == b"EOF":
            return None

        # Divide o pacote em cabeçalho (sequência) e mensagem
        header, msg = data.split(b'|', 1)
        seq_num_received = int(header.decode('utf-8'))
        content = msg  # Conteúdo efetivo do pacote

        # Verifica se o número de sequência recebido é o esperado
        if seq_num_received == seq_num_expected[0]:
            # Envia ACK confirmando pacote correto
            receiver_socket.sendto(f"ACK{seq_num_expected[0]}".encode('utf-8'), address)
            # Alterna o número de sequência para o próximo
            seq_num_expected[0] = 1 - seq_num_expected[0]
            return content  # Retorna a mensagem recebida
        else:
            # Número de sequência inesperado, ACK correspondente para avisar problema
            receiver_socket.sendto(f"ACK{seq_num_received}".encode('utf-8'), address)
            return None  # Descarta esse pacote fora de ordem
    except ConnectionResetError:
        print("Erro: A conexão foi fechada pelo cliente. Finalizando...")
        return None