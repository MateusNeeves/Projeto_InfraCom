import socket
import random
from threading import Thread
from rdt3_0 import send
from rdt3_0 import receive

serverName = "localhost"
serverPort = 12000
buffer_size = 1024
clientList = {} # {username: (address, port)}
onlineClients = {} # {username: {"seq_num_expected": int}}"}
friendsList = {} # {username: {friends}}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((serverName, serverPort))

def main():
    print("Servidor pronto para receber conexões.")
    count = [0]

    while True:
        data, client_address = server_socket.recvfrom(buffer_size)
        Thread(target=receive_from_client, args=(data, client_address, count)).start()

def receive_from_client(data, client_address, count):
    count[0] += 1
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 12000+count[0]))

    username = find_username_by_address(client_address)
    if username in onlineClients:
        seq_num_expected = onlineClients[username]["seq_num_expected"]
        seq_num_expected = [seq_num_expected]
    else:
        seq_num_expected = [0]

    # print(f"Recebido: '{data.decode('utf-8')}' de '{client_address}'")
    cmd = receive(seq_num_expected, data, server_socket, client_address)

    if username in onlineClients:
        onlineClients[username]["seq_num_expected"] = seq_num_expected[0]

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
        follow_cmd(skt, cmd, client_address)
    elif cmd[0] == 'unfollow':
        unfollow_cmd(skt, cmd, client_address)
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
        send([0], "Username já está está sendo utilizado", skt, (client_address[0], client_address[1]+1))
    else:
        clientList[cmd[1]] = client_address
        onlineClients[cmd[1]] = {"seq_num_expected": 1}
        friendsList[cmd[1]] = set()
        send([0], f"Login efetuado com sucesso em {cmd[1]}", skt, (client_address[0], client_address[1]+1))

def logout_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if username in onlineClients:
        del onlineClients[username]
        send([0], f"Logout efetuado com sucesso de {username}", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], "Você não está logado nesse usuário", skt, (client_address[0], client_address[1]+1))

def follow_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if cmd[1] not in clientList:
        send([0], f"Usuário [{cmd[1]}] não encontrado", skt, (client_address[0], client_address[1]+1))
    elif cmd[1] not in friendsList[username]:
        friendsList[username].add(cmd[1])

        send([0], f"[{cmd[1]}] foi adicionado a sua lista de amigos seguidos", skt, (client_address[0], client_address[1]+1))
        if cmd[1] in onlineClients:
            send([0], f"Você foi seguido por [{username}/{client_address[0]}:{client_address[1]}]", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
    else:
        send([0], f"Você já está seguindo [{cmd[1]}].", skt, (client_address[0], client_address[1]+1))

def unfollow_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)

    if cmd[1] in friendsList[username]:
        friendsList[username].remove(cmd[1])
        send([0], f"[{cmd[1]}] foi removido da sua lista de amigos seguidos", skt, (client_address[0], client_address[1]+1))
        if cmd[1] in onlineClients:
            send([0], f"[{username}/{client_address[0]}:{client_address[1]}] deixou de seguir você", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
    else:
        send([0], f"Você não está seguindo [{cmd[1]}]", skt, (client_address[0], client_address[1]+1))

main()
