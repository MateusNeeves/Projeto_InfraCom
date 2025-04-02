import socket
import random
import string
from threading import Thread
from rdt3_0 import send
from rdt3_0 import receive

serverName = "localhost"
serverPort = 12000
buffer_size = 1024
clientList = {} # {username: (address, port)}
onlineClients = {} # {username: {"seq_num_expected": int}}"}
friendsList = {} # {username: {friends}}
groups = {} # {group_id: {"name": str, "key": str, "owner": str, "members": {usersname}}}

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
        list_cinners_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:friends':
        list_friends_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:mygroups':
        pass
    elif cmd[0] == 'list:groups':
        pass
    elif cmd[0] == 'follow':
        follow_cmd(skt, cmd, client_address)
    elif cmd[0] == 'unfollow':
        unfollow_cmd(skt, cmd, client_address)
    elif cmd[0] == 'create_group':
        create_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'delete_group':
        pass
    elif cmd[0] == 'join':
        join_group_cmd(skt, cmd, client_address)
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

def check_group_existance(group_name, username):
    for group_id, group in groups.items():
        if group["name"] == group_name and username in group["members"].keys():
            return True
    return False

def login_cmd(skt, cmd, client_address):
    if cmd[1] in clientList and cmd[1] in onlineClients:
        send([0], "Username já está está sendo utilizado\n", skt, (client_address[0], client_address[1]+1))
    else:
        clientList[cmd[1]] = client_address
        onlineClients[cmd[1]] = {"seq_num_expected": 1}
        friendsList[cmd[1]] = set()
        send([0], f"Login efetuado com sucesso em [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def logout_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if username in onlineClients:
        del onlineClients[username]
        send([0], f"Logout efetuado com sucesso de [{username}]\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], "Você não está logado nesse usuário\n", skt, (client_address[0], client_address[1]+1))

def follow_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if cmd[1] not in clientList:
        send([0], f"Usuário [{cmd[1]}] não encontrado\n", skt, (client_address[0], client_address[1]+1))
    elif cmd[1] not in friendsList[username]:
        friendsList[username].add(cmd[1])

        send([0], f"[{cmd[1]}] foi adicionado a sua lista de amigos seguidos\n", skt, (client_address[0], client_address[1]+1))
        if cmd[1] in onlineClients:
            send([0], f"Você foi seguido por [{username}/{client_address[0]}:{client_address[1]}]\n", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
    else:
        send([0], f"Você já está seguindo [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def unfollow_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)

    if cmd[1] in friendsList[username]:
        friendsList[username].remove(cmd[1])
        send([0], f"[{cmd[1]}] foi removido da sua lista de amigos seguidos\n", skt, (client_address[0], client_address[1]+1))
        if cmd[1] in onlineClients:
            send([0], f"[{username}/{client_address[0]}:{client_address[1]}] deixou de seguir você\n", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
    else:
        send([0], f"Você não está seguindo [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def list_cinners_cmd(skt, cmd, client_address):
    data = "Usuários Online:\n"
    
    for user in onlineClients:
        data += "- " + user + "\n"
    
    send([0], data, skt, (client_address[0], client_address[1]+1))

def list_friends_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    data = "Lista de amigos seguidos:\n"

    if not friendsList[username]:
        send([0], "A lista de amigos seguidos está vazia.\n", skt, (client_address[0], client_address[1]+1))
        return

    for user in friendsList[username]:
        data += "- " + user + "\n"
    
    send([0], data, skt, (client_address[0], client_address[1]+1))

def create_group_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if not check_group_existance(cmd[1], username):
        group_name = cmd[1]
        group_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        members = {}
        members[username] = client_address
        groups[group_id] = {"name": group_name, "owner": username, "members": members}
        send([0], f"O grupo de nome [{group_name}] foi criado com sucesso!\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], f"Você já está em um grupo com o nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def join_group_cmd(skt, cmd, client_address):
    username = find_username_by_address(client_address)
    if not check_group_existance(cmd[1], username):
        for group_id, group in groups.items():
            if group["name"] == cmd[1] and group_id == cmd[2]:
                group["members"][username] = client_address
                send([0], f"Você entrou no grupo de nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))
                for member, addr in group["members"].items():
                    if member != username:
                        send([0], f"[{username}/{client_address[0]}:{client_address[1]}] acabou de entrar no grupo\n", skt, (addr[0], addr[1]+1))
                return
    else:
        send([0], f"Você já está em um grupo com o nome: [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))


main()
