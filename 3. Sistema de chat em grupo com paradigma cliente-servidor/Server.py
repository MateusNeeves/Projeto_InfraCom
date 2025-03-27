import socket
import random
from threading import Thread
from rdt3_0 import send
from rdt3_0 import receive

serverName = "localhost"
serverPort = 12000
buffer_size = 1024
clientList = {} # {username: (address, port)}
onlineClients = {} # {username: (address, port)}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((serverName, serverPort))
seq_num_expected = [0]

def main():
    print("Servidor pronto para receber arquivos.")
    count = [0]

    while True:
        data, client_address = server_socket.recvfrom(buffer_size)
        Thread(target=receive_from_client, args=(data, client_address, count)).start()

def receive_from_client(data, client_address, count):
    count[0] += 1
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 12000+count[0]))

    print(f"Recebido: '{data.decode('utf-8')}' de '{client_address}'")
    cmd = receive(seq_num_expected, data, server_socket, client_address)

    if cmd is None:
        return

    cmd = cmd.decode('utf-8').split(' ', 3)

    if cmd[0] == 'login':
        login_cmd(skt, cmd, client_address)
    elif cmd[0] == 'logout':
        logout_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:cinners':
        pass
    elif cmd[0] == 'list:friends':
        pass
    elif cmd[0] == 'list:mygroups':
        pass
    elif cmd[0] == 'list:groups':
        pass
    elif cmd[0] == 'follow':
        pass
    elif cmd[0] == 'unfollow':
        pass
    elif cmd[0] == 'create_group':
        pass
    elif cmd[0] == 'delete_group':
        pass
    elif cmd[0] == 'join':
        pass
    elif cmd[0] == 'leave':
        pass
    elif cmd[0] == 'ban':
        pass
    elif cmd[0] == 'chat_group':
        pass
    elif cmd[0] == 'chat_friend':
        pass

def find_username_by_address(addr):
    for username, client_addr in clientList.items():
        if client_addr == addr:
            return username
    return None

def login_cmd(skt, cmd, client_address):
    if cmd[1] in clientList and cmd[1] in onlineClients:
        send([0], "Username já está está sendo utilizado.", skt, (client_address[0], client_address[1]+1))
    else:
        clientList[cmd[1]] = client_address
        onlineClients[cmd[1]] = client_address
        send([0], f"Login efetuado com sucesso em {cmd[1]}", skt, (client_address[0], client_address[1]+1))

def logout_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if username in onlineClients:
        del onlineClients[username]
        send([0], f"Logout efetuado com sucesso de {username}", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], "Você não está logado nesse usuário.", skt, (client_address[0], client_address[1]+1))

main()
