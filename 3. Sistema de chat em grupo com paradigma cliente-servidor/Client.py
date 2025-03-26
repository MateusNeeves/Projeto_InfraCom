import socket
import os
import random
import time
from sender_rdt3 import send

serverName = "localhost"
serverPort = 12000
buffer_size = 1024  # Tamanho do buffer

def login_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'login' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print("Logando...")
        send(" ".join(cmd), serverPort)

def logout_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'logout' não requer argumentos!")
    else:
        print("Deslogando...")
        send(" ".join(cmd), serverPort)
        
def list_cinners_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:cinners' não requer argumentos!")
    else:
        print("Carregando lista de usuários conectados...")
        send(" ".join(cmd), serverPort)

def list_friends_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:friends' não requer argumentos!")
    else:
        print("Carregando lista de amigos...")
        send(" ".join(cmd), serverPort)

def list_mygroups_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:mygroups' não requer argumentos!")
    else:
        print("Carregando lista de grupos que vocë faz parte...")
        send(" ".join(cmd), serverPort)

def list_groups_cmd(cmd):
    if len(cmd) > 1:
        print("Comando 'list:groups' não requer argumentos!")
    else:
        print("Carregando lista de grupos que vocë criou...")
        send(" ".join(cmd), serverPort)

def follow_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'follow' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print(f"Seguindo {cmd[1]}...")
        send(" ".join(cmd), serverPort)

def unfollow_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'unfollow' requer um nome de usuário!")
    elif len(cmd) > 2:
        print("Nome de usuário não pode conter espaços!")
    else:
        print(f"Deixando de seguir {cmd[1]}...")
        send(" ".join(cmd), serverPort)

def create_group_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'create_group' requer o nome do grupo!")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Criando grupo '{cmd[1]}'...")
        send(" ".join(cmd), serverPort)

def delete_group_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'delete_group' requer o nome do grupo!")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Deletando grupo '{cmd[1]}'...")
        send(" ".join(cmd), serverPort)

def join_cmd(cmd):
    if len(cmd) < 3:
        print("Comando 'join' requer o nome do grupo e a chave do grupo!")
    elif len(cmd) > 3:
        print("Nome do grupo e chave do grupo não podem conter espaços!")
    else:
        print(f"Entrando no grupo '{cmd[1]}' - '{cmd[2]}'...")
        send(" ".join(cmd), serverPort)

def leave_cmd(cmd):
    if len(cmd) < 2:
        print("Comando 'leave' requer o nome do grupo")
    elif len(cmd) > 2:
        print("Nome do grupo não pode conter espaços!")
    else:
        print(f"Saindo do grupo '{cmd[1]}'...")
        send(" ".join(cmd), serverPort)

def chat_group_cmd(cmd):
    if len(cmd) < 3:
        print("Comando 'chat_group' requer o nome do grupo, a chave do grupo e a mensagem a ser enviada")
    else:
        print(f"Enviando mensagem no grupo '{cmd[1]}' - '{cmd[2]}'...")
        send(" ".join(cmd), serverPort)

def chat_friend_cmd(cmd):
    if len(cmd) < 3:
        print("Comando 'chat_friend' requer o nome do akmigo e a mensagem a ser enviada")
    else:
        print(f"Enviando mensagem ao amigo '{cmd[1]}'...")
        send(" ".join(cmd), serverPort)

while True:
    print("Digite o comando:")
    cmd = input().split()

    if cmd[0] == 'login':
        login_cmd(cmd)
    elif cmd[0] == 'logout':
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

  