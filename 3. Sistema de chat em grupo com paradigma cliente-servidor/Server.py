import socket
import datetime
from threading import Thread
from rdt3_0 import send, receive

# Configurações do servidor
serverName = "localhost"
serverPort = 12000
buffer_size = 1024

# Dicionários para gerenciar usuários, conexões, amigos e grupos
clientList = {}    # {username: (address, port)}
onlineClients = {} # {username: {"seq_num_expected": int}}
friendsList = {}   # {username: {friends}}
groups = {}        # {group_id: {"name": str, "owner": str, "members": {username: (addr,port)}}}

# Cria socket e estabelece porta para o servidor
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((serverName, serverPort))

def main():
    # Mensagem de prontidão do servidor
    print("Servidor pronto para receber conexões.")
    count = [0]  # Contador de conexões, usado para criar portas únicas para cada thread

    while True:
        data, client_address = server_socket.recvfrom(buffer_size)  # Aguarda dados de qualquer cliente
        Thread(target=receive_from_client, args=(data, client_address, count)).start()

def receive_from_client(data, client_address, count):
    # Incrementa o contador para cada nova conexão, criando porta exclusiva
    count[0] += 1
    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(("localhost", 12000 + count[0]))

    # Verifica username associado ao endereço
    username = find_username_by_address(client_address)
    if username in onlineClients:
        seq_num_expected = onlineClients[username]["seq_num_expected"]
        seq_num_expected = [seq_num_expected]
    else:
        seq_num_expected = [0]

    # Recebe comando usando o protocolo de transferência confiável
    cmd = receive(seq_num_expected, data, server_socket, client_address)
    if username in onlineClients:
        # Atualiza o seq_num_expected desse usuário
        onlineClients[username]["seq_num_expected"] = seq_num_expected[0]

    # Se comando é inválido ou nulo, interrompe execução
    if cmd is None:
        return

    # Trata partes do comando (diferencia mensagens com mais espaços)
    parts = cmd.decode('utf-8').split(' ', 3)
    if len(parts) >= 4 and parts[0] == "chat_group":
        mensagem = " ".join(parts[3:])
        cmd = [parts[0], parts[1], parts[2], mensagem]
    elif len(parts) >= 3 and parts[0] == "chat_friend":
        mensagem = " ".join(parts[2:])
        cmd = [parts[0], parts[1], mensagem]
    else:
        cmd = parts

    # Direciona cada tipo de comando para a função correspondente
    if cmd[0] == 'login':
        login_cmd(skt, cmd, client_address)
    elif cmd[0] == 'logout':
        logout_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:cinners':
        list_cinners_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:friends':
        list_friends_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:mygroups':
        list_mygroups_cmd(skt, cmd, client_address)
    elif cmd[0] == 'list:groups':
        list_groups_cmd(skt, cmd, client_address)
    elif cmd[0] == 'follow':
        follow_cmd(skt, cmd, client_address)
    elif cmd[0] == 'unfollow':
        unfollow_cmd(skt, cmd, client_address)
    elif cmd[0] == 'create_group':
        create_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'delete_group':
        delete_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'join':
        join_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'leave':
        leave_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'ban':
        ban_cmd(skt, cmd, client_address)
    elif cmd[0] == 'chat_group':
        chat_group_cmd(skt, cmd, client_address)
    elif cmd[0] == 'chat_friend':
        chat_friend_cmd(skt, cmd, client_address)

def find_username_by_address(addr):
    # Retorna o username vinculado a um endereço específico
    for username, client_addr in clientList.items():
        if client_addr == addr:
            return username
    return None

def check_group_member(group_name, username):
    # Verifica se um usuário faz parte de um grupo
    for group_id, group in groups.items():
        if group["name"] == group_name and username in group["members"].keys():
            return True
    return False

def find_group_by_name(group_name, username):
    # Localiza o ID do grupo a partir do nome, se o usuário pertencer a ele
    for group_id, group in groups.items():
        if group["name"] == group_name and username in group["members"].keys():
            return group_id
    return None

def check_key_existance(group_key):
    # Verifica se a chave do grupo já existe
    for group_id, group in groups.items():
        if group_id == group_key:
            return True
    return False

def login_cmd(skt, cmd, client_address):
    # Faz login de um usuário, adicionando-o aos registradores de clientes
    if cmd[1] in clientList and cmd[1] in onlineClients:
        send([0], "Username já está está sendo utilizado\n", skt, (client_address[0], client_address[1]+1))
    else:
        clientList[cmd[1]] = client_address
        onlineClients[cmd[1]] = {"seq_num_expected": 1}
        friendsList[cmd[1]] = set()
        send([0], f"Login efetuado com sucesso em [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def logout_cmd(skt, cmd, client_address):
    # Faz logout de um usuário, removendo-o dos registradores
    username = find_username_by_address(client_address)
    if username in onlineClients:
        del onlineClients[username]
        send([0], f"Logout efetuado com sucesso de [{username}]\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], "Você não está logado nesse usuário\n", skt, (client_address[0], client_address[1]+1))

def follow_cmd(skt, cmd, client_address):
    # Segue um usuário (adiciona usuário desejado à lista de amigos)
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
    # Deixa de seguir um usuário, removendo da lista de amigos
    username = find_username_by_address(client_address)
    if cmd[1] in friendsList[username]:
        friendsList[username].remove(cmd[1])
        send([0], f"[{cmd[1]}] foi removido da sua lista de amigos seguidos\n", skt, (client_address[0], client_address[1]+1))
        if cmd[1] in onlineClients:
            send([0], f"[{username}/{client_address[0]}:{client_address[1]}] deixou de seguir você\n", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
    else:
        send([0], f"Você não está seguindo [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def list_cinners_cmd(skt, cmd, client_address):
    # Lista todos os usuários atualmente online
    data = "Usuários Online:\n"
    for user in onlineClients:
        data += "- " + user + "\n"
    send([0], data, skt, (client_address[0], client_address[1]+1))

def list_friends_cmd(skt, cmd, client_address):
    # Lista amigos que o usuário logado está seguindo
    username = find_username_by_address(client_address)
    data = "Lista de amigos seguidos:\n"
    if not friendsList[username]:
        send([0], "A lista de amigos seguidos está vazia.\n", skt, (client_address[0], client_address[1]+1))
        return
    for user in friendsList[username]:
        data += "- " + user + "\n"
    send([0], data, skt, (client_address[0], client_address[1]+1))

def list_mygroups_cmd(skt, cmd, client_address):
    # Lista grupos criados pelo usuário logado
    username = find_username_by_address(client_address)
    data = "Grupos que você criou:\n"
    has_groups = False
    for group_id, group in groups.items():
        if group["owner"] == username:
            has_groups = True
            data += "- " + group["name"] + " (" + group_id + ")\n"
    if not has_groups:
        data = "Você não criou nenhum grupo.\n"
    send([0], data, skt, (client_address[0], client_address[1]+1))

def list_groups_cmd(skt, cmd, client_address):
    # Lista grupos em que o usuário faz parte
    username = find_username_by_address(client_address)
    data = "Grupos que você participa:\n"
    has_groups = False
    for group_id, group in groups.items():
        if username in group["members"].keys():
            has_groups = True
            data += "- " + group["name"] + ' - ' + group["created_at"].strftime("%d/%m/%Y %H:%M:%S") + ' (' + group["owner"] + ')\n'
    if not has_groups:
        data = "Você não participa de nenhum grupo.\n"
    send([0], data, skt, (client_address[0], client_address[1]+1))

def delete_group_cmd(skt, cmd, client_address):
    # Exclui um grupo, se o usuário for dono do mesmo
    username = find_username_by_address(client_address)
    group_id = find_group_by_name(cmd[1], username)
    if group_id is not None:
        if groups[group_id]["owner"] == username:
            members = groups[group_id]["members"].copy()
            del groups[group_id]
            send([0], f"Grupo de nome [{cmd[1]}] foi deletado com sucesso!\n", skt, (client_address[0], client_address[1]+1))
            # Notifica outros membros que o grupo foi deletado
            for member, addr in members.items():
                if member != username:
                    send([0], f"[{username}/{client_address[0]}:{client_address[1]}] deletou o grupo [{cmd[1]}]\n", skt, (addr[0], addr[1]+1))
        else:
            send([0], f"Você não é o dono do grupo de nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], f"Grupo de nome [{cmd[1]}] não encontrado\n", skt, (client_address[0], client_address[1]+1))

def create_group_cmd(skt, cmd, client_address):
    # Cria um grupo com nome e chave, se não existir outro com a mesma chave
    username = find_username_by_address(client_address)
    if check_key_existance(cmd[2]):
        send([0], f"Já existe um grupo com a chave [{cmd[2]}]\n", skt, (client_address[0], client_address[1]+1))
    elif not check_group_member(cmd[1], username):
        group_name = cmd[1]
        group_id = cmd[2]
        created_at = datetime.datetime.now()
        members = {username: client_address}
        groups[group_id] = {"name": group_name, "owner": username, "created_at": created_at, "members": members}
        send([0], f"O grupo de nome [{group_name}] foi criado com sucesso!\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], f"Você já está em um grupo com o nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def join_group_cmd(skt, cmd, client_address):
    # Entra em um grupo se estiver com a chave correta e não for membro
    username = find_username_by_address(client_address)
    if not check_group_member(cmd[1], username):
        for group_id, group in groups.items():
            if group["name"] == cmd[1] and group_id == cmd[2]:
                group["members"][username] = client_address
                send([0], f"Você entrou no grupo de nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))
                # Notifica os demais membros sobre a entrada
                for member, addr in group["members"].items():
                    if member != username:
                        send([0], f"[{username}/{client_address[0]}:{client_address[1]}] acabou de entrar no grupo [{cmd[1]}]\n", skt, (addr[0], addr[1]+1))
                return
        send([0], f"Grupo de nome [{cmd[1]}] não encontrado\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], f"Você já está em um grupo com o nome: [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def leave_group_cmd(skt, cmd, client_address):
    # Sai de um grupo caso o usuário faça parte dele
    username = find_username_by_address(client_address)
    group_id = find_group_by_name(cmd[1], username)
    if group_id is not None:
        del groups[group_id]["members"][username]
        send([0], f"Você saiu do grupo de nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))
        # Notifica demais usuários sobre a saída
        for member, addr in groups[group_id]["members"].items():
            send([0], f"[{username}/{client_address[0]}:{client_address[1]}] saiu do grupo [{cmd[1]}]\n", skt, (addr[0], addr[1]+1))
    else:
        send([0], f"Você não está no grupo de nome [{cmd[1]}]\n", skt, (client_address[0], client_address[1]+1))

def ban_cmd(skt, cmd, client_address):
    # Bane um usuário do grupo, caso o solicitante seja o dono
    username = find_username_by_address(client_address)
    ban_username = cmd[1]
    group_id = find_group_by_name(cmd[2], username)
    if group_id is not None:
        if username is not groups[group_id]["owner"]:
            send([0], f"Você não é administrador do grupo de nome [{cmd[2]}]\n", skt, (client_address[0], client_address[1]+1))
        else:
            if ban_username not in groups[group_id]["members"]:
                send([0], f"Usuário [{cmd[1]}] não está no grupo de nome [{cmd[2]}]\n", skt, (client_address[0], client_address[1]+1))
            else:
                del groups[group_id]["members"][ban_username]
                send([0], f"[{username}/{client_address[0]}:{client_address[1]}] o adiministrador do grupo [{cmd[2]}] o baniu!\n", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
                for member, addr in groups[group_id]["members"].items():
                    send([0], f"[{ban_username}] foi banido do grupo [{cmd[2]}]\n", skt, (addr[0], addr[1]+1))
    else:
        send([0], f"Você não está no grupo de nome [{cmd[2]}]\n", skt, (client_address[0], client_address[1]+1))

def chat_friend_cmd(skt, cmd, client_address):
    # Envia mensagem diretamente a um amigo
    username = find_username_by_address(client_address)
    if cmd[1] not in clientList:
        send([0], f"Usuário [{cmd[1]}] não encontrado\n", skt, (client_address[0], client_address[1]+1))
    elif cmd[1] not in friendsList[username]:
        send([0], f"Amigo [{cmd[1]}] não encontrado\n", skt, (client_address[0], client_address[1]+1))
    else:
        send([0], f"[{username}/{client_address[0]}:{client_address[1]}] [{cmd[2]}]\n", skt, (clientList[cmd[1]][0], clientList[cmd[1]][1]+1))
        send([0], "Mensagem Enviada\n", skt, (client_address[0], client_address[1]+1))

def chat_group_cmd(skt, cmd, client_address):
    # Envia mensagem para todos do grupo, caso o usuário pertença ao grupo correto
    username = find_username_by_address(client_address)
    group_id = find_group_by_name(cmd[1], username)
    if group_id is None or cmd[2] != group_id:
        send([0], f"Você [{username}] não está no grupo de nome [{cmd[1]}] e ID:[{cmd[2]}]\n", skt, (client_address[0], client_address[1]+1))
    else:
        for member, addr in groups[group_id]["members"].items():
            if username != member:
                send([0], f"[{username}/{client_address[0]}:{client_address[1]}] em [{cmd[1]}]:[{cmd[3]}]\n", skt, (addr[0], addr[1]+1))
        send([0], f"Mensagem Enviada no grupo [{cmd[1]}]", skt, (client_address[0], client_address[1]+1))

# Inicia o servidor
main()

