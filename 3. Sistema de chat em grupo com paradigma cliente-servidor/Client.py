import socket
import os
import time
from threading import Thread, Event
from rdt3_0 import send
from rdt3_0 import receive

serverName = "localhost"
serverPort = 12000
buffer_size = 1024  # Tamanho do buffer
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(("localhost", 0))
client_socket.settimeout(1)  # Timeout para retransmissão
seq_num = [0]
loggedUsername = None
login_event = Event()

def main():
    Thread(target=receive_message).start()
    while True:

        print("Digite o comando:")
        cmd = input().split(' ', 3)

        if cmd[0] == 'login':
            if loggedUsername:
                print(f"Você já está logado como {loggedUsername}!")
            else:
                login_cmd(cmd)
                
                
        elif not loggedUsername:
            print("Você precisa estar logado para executar comandos!")
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
                print(f"Comando '{cmd[0]}' não existe!")


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
            print(message)
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
        except OSError as e:
            print(f"Erro ao receber mensagem: {e}")
            break

def login_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'login' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print("Logando...")
        login_event.clear()
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        login_event.wait()

def logout_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'logout' não requer argumentos!")
    else:
        print("Deslogando...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))
        
def list_cinners_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:cinners' não requer argumentos!")
    else:
        print("Carregando lista de usuários conectados...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def list_friends_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:friends' não requer argumentos!")
    else:
        print("Carregando lista de amigos...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def list_mygroups_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:mygroups' não requer argumentos!")
    else:
        print("Carregando lista de grupos que vocë faz parte...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def list_groups_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:groups' não requer argumentos!")
    else:
        print("Carregando lista de grupos que vocë criou...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def follow_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'follow' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print(f"Seguindo {cmd[1]}...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def unfollow_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'unfollow' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print(f"Deixando de seguir {cmd[1]}...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def create_group_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'create_group' requer o nome do grupo!")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Criando grupo '{cmd[1]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def delete_group_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'delete_group' requer o nome do grupo!")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Deletando grupo '{cmd[1]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def join_cmd(cmd):
    if len(cmd) < 3:
        print("Comando 'join' requer o nome do grupo e a chave do grupo!")
    elif len(cmd) > 3:
        print("Nome do grupo e chave do grupo não podem conter espaços!")
    else:
        print(f"Entrando no grupo '{cmd[1]}' - '{cmd[2]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def leave_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'leave' requer o nome do grupo")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Saindo do grupo '{cmd[1]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def chat_group_cmd(cmd):
    if len(cmd) < 4:
        print("Comando 'chat_group' requer o nome do grupo, a chave do grupo e a mensagem a ser enviada")
    else:
        print(f"Enviando mensagem no grupo '{cmd[1]}' - '{cmd[2]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

def chat_friend_cmd(cmd):
    if len(cmd) < 3:
        print("Comando 'chat_friend' requer o nome do amigo e a mensagem a ser enviada")
    else:
        print(f"Enviando mensagem ao amigo '{cmd[1]}'...")
        send(seq_num, " ".join(cmd), client_socket, (serverName, serverPort))

main()