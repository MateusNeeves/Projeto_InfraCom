import socket
from threading import Thread, Event
from rdt3_0 import send
from rdt3_0 import receive
from colorama import Fore, init

# Inicializa a biblioteca colorama para funcionar corretamente no Windows
init(autoreset=True)

# Nome do servidor e porta do servidor para conexão
serverName = "localhost"
serverPort = 12000
buffer_size = 1024  # Tamanho máximo do buffer para recebimento de dados

# Cria socket UDP e faz o bind em uma porta aleatória (0) para o cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("localhost", 0))
client_socket.settimeout(1)  # Tempo de espera para recv (timeout em segundos)

seq_num = [0]         # Número de sequência no protocolo RDT
loggedUsername = None # Armazena o nome do usuário logado
login_event = Event() # Evento para sincronizar login
sync_msg_event = Event() # Evento para sincronizar mensagens

def main():
    # Inicia uma thread dedicada para receber mensagens
    Thread(target=receive_message).start()

    # Mensagem inicial para o usuário
    print(Fore.CYAN + "Digite o comando:")

    # Loop principal para capturar comandos do usuário
    while True:
        parts = input().split(' ')  # Divide a entrada por espaços

        # Tratamento especial de comandos que contêm mais partes (mensagens de texto)
        if len(parts) >= 4 and parts[0] == "chat_group":
            mensagem = " ".join(parts[3:])  # Une as partes em uma só string
            cmd = [parts[0], parts[1], parts[2], mensagem]
        elif len(parts) >= 3 and parts[0] == "chat_friend":
            mensagem = " ".join(parts[2:])
            cmd = [parts[0], parts[1], mensagem]
        else:
            cmd = parts

        # Verifica se é comando de login
        if cmd[0] == 'login':
            if loggedUsername:
                # Usuário já está logado
                print(Fore.YELLOW + f"Você já está logado como {loggedUsername}!\n")
                print(Fore.CYAN + "Digite o comando:")
            else:
                login_cmd(cmd)
        # Se não está logado e não é comando de login, usuário não pode executar
        elif not loggedUsername:
            print(Fore.RED + "Você precisa estar logado para executar comandos!\n")
            print(Fore.CYAN + "Digite o comando:")
        else:
            # Trata outros comandos caso o usuário já esteja logado
            if cmd[0] == 'logout':
                logout_cmd(cmd)
            elif cmd[0] == 'list:cinners':
                list_cinners_cmd(cmd)
            elif cmd[0] == 'list:friends':
                list_friends_cmd(cmd)
            elif cmd[0] == 'list:mygroups':
                list_mygroups_cmd(cmd)
            elif cmd[0] == 'list:groups':
                list_groups_cmd(cmd)
            elif cmd[0] == 'follow':
                # Evita que o usuário siga a si mesmo
                if cmd[1] == loggedUsername:
                    print(Fore.RED + "Você não pode seguir a si mesmo!\n")
                    print(Fore.CYAN + "Digite o comando:")
                else:
                    follow_cmd(cmd)
            elif cmd[0] == 'unfollow':
                unfollow_cmd(cmd)
            elif cmd[0] == 'create_group':
                create_group_cmd(cmd)
            elif cmd[0] == 'delete_group':
                delete_group_cmd(cmd)
            elif cmd[0] == 'join':
                join_cmd(cmd)
            elif cmd[0] == 'leave':
                leave_cmd(cmd)
            elif cmd[0] == 'ban':
                ban_cmd(cmd)
            elif cmd[0] == 'chat_group':
                chat_group_cmd(cmd)
            elif cmd[0] == 'chat_friend':
                chat_friend_cmd(cmd)
            else:
                # Comando não reconhecido
                print(Fore.RED + f"Comando '{cmd[0]}' não existe!\n")
                print(Fore.CYAN + "Digite o comando:")

def receive_message():
    """
    Thread que fica em loop, esperando por mensagens do servidor
    """
    # Cria socket adicional para receber dados em porta adjacente
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", client_socket.getsockname()[1]+1))

    while True:
        try:
            data, client_address = skt.recvfrom(buffer_size)
            # Tenta receber a mensagem usando o protocolo RDT
            message = receive([0], data, skt, client_address)

            if message == None:
                continue  # Se não houve mensagem válida, pula

            message = message.decode('utf-8')
            print(Fore.MAGENTA + message)  # Exibe mensagem recebida

            # Verifica possíveis respostas do servidor
            if message.startswith("Login efetuado com sucesso"):
                global loggedUsername
                loggedUsername = message.split()[-1]
                login_event.set()
            elif message.startswith("Logout efetuado com sucesso"):
                loggedUsername = None
                seq_num[0] = 0
                login_event.set()
            elif message.startswith("Username já está está sendo utilizado"):
                seq_num[0] = 0
                login_event.set()
            elif message.startswith("Você não está logado nesse usuário"):
                seq_num[0] = 0
                login_event.set()

            print(Fore.CYAN + "Digite o comando:")
            sync_msg_event.set()  # Libera eventos para sincronizar
        except OSError as e:
            # Erro de socket ou timeout
            print(Fore.YELLOW + f"Erro ao receber mensagem: {e}\n")
            print(Fore.CYAN + "Digite o comando:")
            break

def login_cmd(cmd):
    """
    Tenta realizar login do usuário.
    Formato esperado: login <username>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'login' requer um nome de usuário!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome de usuário não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Logando...")
        login_event.clear()
        # Envia comando ao servidor via RDT
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        login_event.wait()

def logout_cmd(cmd):
    """
    Desconecta o usuário atual do servidor.
    Formato esperado: logout
    """
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'logout' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Deslogando...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_cinners_cmd(cmd):
    """
    Lista todos os usuários conectados (cinners).
    Formato esperado: list:cinners
    """
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:cinners' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de usuários conectados...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_friends_cmd(cmd):
    """
    Lista todos os amigos do usuário logado.
    Formato esperado: list:friends
    """
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:friends' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de amigos...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_mygroups_cmd(cmd):
    """
    Lista os grupos criados pelo usuário logado.
    Formato esperado: list:mygroups
    """
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:mygroups' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de grupos que você criou...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_groups_cmd(cmd):
    """
    Lista os grupos do qual o usuário logado faz parte.
    Formato esperado: list:groups
    """
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:groups' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de grupos que você faz parte...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def follow_cmd(cmd):
    """
    Solicita seguir um outro usuário.
    Formato esperado: follow <username>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'follow' requer um nome de usuário!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome de usuário não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Seguindo {cmd[1]}...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def unfollow_cmd(cmd):
    """
    Solicita deixar de seguir um usuário.
    Formato esperado: unfollow <username>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'unfollow' requer um nome de usuário!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome de usuário não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Deixando de seguir {cmd[1]}...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def create_group_cmd(cmd):
    """
    Cria um novo grupo.
    Formato esperado: create_group <nomeDoGrupo> <chaveDoGrupo>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'create_group' requer o nome do grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) < 3:
        print(Fore.RED + "Comando 'create_group' requer o nome do grupo e a chave do grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 3:
        print(Fore.RED + "Nome do grupo não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Criando grupo '{cmd[1]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def delete_group_cmd(cmd):
    """
    Exclui um grupo existente.
    Formato esperado: delete_group <nomeDoGrupo>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'delete_group' requer o nome do grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome do grupo não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Deletando grupo '{cmd[1]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def join_cmd(cmd):
    """
    Entra em um grupo existente.
    Formato esperado: join <nomeDoGrupo> <chaveDoGrupo>
    """
    if len(cmd) < 3:
        print(Fore.RED + "Comando 'join' requer o nome do grupo e a chave do grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 3:
        print(Fore.RED + "Nome do grupo e chave do grupo não podem conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Entrando no grupo '{cmd[1]}' - '{cmd[2]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def leave_cmd(cmd):
    """
    Sai de um grupo existente.
    Formato esperado: leave <nomeDoGrupo>
    """
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'leave' requer o nome do grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome do grupo não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Saindo do grupo '{cmd[1]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def chat_group_cmd(cmd):
    """
    Envia mensagem para um grupo.
    Formato esperado: chat_group <nomeDoGrupo> <chaveDoGrupo> <mensagem>
    """
    if len(cmd) < 4:
        print(Fore.RED + "Comando 'chat_group' requer o nome do grupo, a chave do grupo e a mensagem!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Enviando mensagem no grupo '{cmd[1]}' - '{cmd[2]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def chat_friend_cmd(cmd):
    """
    Envia mensagem para um amigo.
    Formato esperado: chat_friend <nomeDoAmigo> <mensagem>
    """
    if len(cmd) < 3:
        print(Fore.RED + "Comando 'chat_friend' requer o nome do amigo e a mensagem!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Enviando mensagem ao amigo '{cmd[1]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def ban_cmd(cmd):
    """
    Bane um usuário de um grupo.
    Formato esperado: ban <nomeDoUsuario> <nomeDoGrupo>
    """
    if len(cmd) < 3:
        print(Fore.RED + "Comando 'ban_cmd' requer o usuário e o grupo!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"'{cmd[1]}' foi banido do grupo")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

# Função principal chamada na execução
main()