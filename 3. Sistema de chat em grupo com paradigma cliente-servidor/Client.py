import socket
import os
import time
from threading import Thread, Event
from rdt3_0 import send
from rdt3_0 import receive
from colorama import Fore, Style, init

# Inicializa o colorama para funcionar no Windows
init(autoreset=True)

serverName = "localhost"
serverPort = 12000
buffer_size = 1024  # Tamanho do buffer
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("localhost", 0))
client_socket.settimeout(1)  # Timeout para retransmissão
seq_num = [0]
loggedUsername = None
login_event = Event()
sync_msg_event = Event()

def main():
    Thread(target=receive_message).start()
    print(Fore.CYAN + "Digite o comando:")
    while True:
        #print(Fore.CYAN + "Digite o comando:")
        cmd = input().split(' ', 3)

        if cmd[0] == 'login':
            if loggedUsername:
                print(Fore.YELLOW + f"Você já está logado como {loggedUsername}!\n")
                print(Fore.CYAN + "Digite o comando:")
            else:
                login_cmd(cmd)

        elif not loggedUsername:
            print(Fore.RED + "Você precisa estar logado para executar comandos!\n")
            print(Fore.CYAN + "Digite o comando:")
        else:
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
                print(Fore.RED + f"Comando '{cmd[0]}' não existe!\n")
                print(Fore.CYAN + "Digite o comando:")
        
        

def receive_message():
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", client_socket.getsockname()[1]+1))
    while True:
        try:
            data, client_address = skt.recvfrom(buffer_size)
            message = receive([0], data, skt, client_address)
            if message == None:
                continue
            message = message.decode('utf-8')
            print(Fore.MAGENTA + message)
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
            sync_msg_event.set()
        except OSError as e:
            print(Fore.YELLOW + f"Erro ao receber mensagem: {e}\n")
            print(Fore.CYAN + "Digite o comando:")
            break

def login_cmd(cmd):
    if len(cmd) < 2:
        print(Fore.RED + "Comando 'login' requer um nome de usuário!\n")
        print(Fore.CYAN + "Digite o comando:")
    elif len(cmd) > 2:
        print(Fore.RED + "Nome de usuário não pode conter espaços!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Logando...")
        login_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        login_event.wait()

def logout_cmd(cmd):
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'logout' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Deslogando...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_cinners_cmd(cmd):
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:cinners' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de usuários conectados...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_friends_cmd(cmd):
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:friends' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de amigos...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_mygroups_cmd(cmd):
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:mygroups' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de grupos que você faz parte...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def list_groups_cmd(cmd):
    if len(cmd) > 1:
        print(Fore.RED + "Comando 'list:groups' não requer argumentos!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + "Carregando lista de grupos que você criou...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def follow_cmd(cmd):
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
    if len(cmd) < 4:
        print(Fore.RED + "Comando 'chat_group' requer o nome do grupo, a chave do grupo e a mensagem a ser enviada!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Enviando mensagem no grupo '{cmd[1]}' - '{cmd[2]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

def chat_friend_cmd(cmd):
    if len(cmd) < 3:
        print(Fore.RED + "Comando 'chat_friend' requer o nome do amigo e a mensagem a ser enviada!\n")
        print(Fore.CYAN + "Digite o comando:")
    else:
        print(Fore.GREEN + f"Enviando mensagem ao amigo '{cmd[1]}'...")
        sync_msg_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        sync_msg_event.wait()

main()