import asyncio
import websockets
import json

USERS = set()
NAMES = set()
USERS_NAMES = dict()

'''Definicoes auxiliares'''
def boas_vindas_aux():
    message = "Bem vindo ao servidor chat escrito em Python com asyncio e WebSockets. Por favor, identifique-se com seu nome (ex: /Nome SeuNome):"
    return json.dumps({"type": "SYSTEM", "message": message})

def nome_repetido_aux():
    message = "Alguém já esta usando esse nome. Por favor insira outro nome (ex: /Nome SeuNome):"
    return json.dumps({"type": "SYSTEM", "message": message})

def sem_nome_aux():
    message = "Você não pode mandar mensagem sem nome. Por favor, insira seu nome (ex: /Nome SeuNome):"
    return json.dumps({"type": "SYSTEM", "message": message})

def registrado_aux(user):
    message = "Nome registrado! Seu nome é %s. \nPara enviar uma mensagem privada, basta seguir o formato: '/Usuario Olá'"%(user)
    return json.dumps({"type": "SYSTEM", "message": message})

def notifica_sala_aux(user):
    message = "%s entrou na sala."%(user)
    return json.dumps({"type": "SYSTEM", "message": message})

def mensagem_publica_aux(message,sender):
    aux = "%s >> %s"%(sender,message)
    return json.dumps({"type": "PUBLIC", "message": aux})

def mensagem_privada_aux(message,sender):
    aux = "%s (mensagem privada) >> %s"%(sender,message)
    return json.dumps({"type": "PRIVATE", "message": aux})

def usuario_nao_encontrado():
    message = "Não encontramos nenhum usuário com esse nome"
    return json.dumps({"type": "SYSTEM", "message": message})


'''Definicoes async'''

async def boas_vindas(connection):
    message = boas_vindas_aux()
    await connection.send(message)

async def registro(connection):
    await boas_vindas(connection)
    while True:
        json_msg = await connection.recv()
        name_aux = json.loads(json_msg)["message"]
        if name_aux.startswith("/Nome "):
            name = name_aux[6:]
            if name not in NAMES:
                break
            else:
                message = nome_repetido_aux()
                await connection.send(message)
        else:
            message = sem_nome_aux()
            await connection.send(message)

    USERS.add(connection)
    NAMES.add(name)
    USERS_NAMES[connection] = name
    await notifica_sala(connection)
    await registrado(connection)

async def sem_nome(connection):
    message = sem_nome_aux()
    await connection.send(message)

async def nome_repetido(connection):
    message = nome_repetido_aux()
    await connection.send(message)

async def registrado(connection):
    message = registrado_aux(USERS_NAMES[connection])
    await connection.send(message)

async def notifica_sala(connection):
    if USERS:
        message = notifica_sala_aux(USERS_NAMES[connection])
        for user in USERS:
            if user != connection:
                await user.send(message)

async def mensagem_publica(connection, message):
    if USERS: 
        message = mensagem_publica_aux(message,USERS_NAMES[connection])
        for user in USERS:
            if user != connection:
                await user.send(message)

async def mensagem_privada(connection, message, receiver):
    if USERS:         
        receiver_connection = None
        for conn, name in USERS_NAMES.items():
            if name == receiver:
                receiver_connection = conn
            
        if receiver_connection:
            message = mensagem_privada_aux(message, USERS_NAMES[connection])
            await receiver_connection.send(message)
        else:
            message = usuario_nao_encontrado()
            await connection.send(message)

async def main(connection, path):
    await registro(connection)
    async for message in connection:
        data = json.loads(message)
        if data["action"] == "public_message":
            await mensagem_publica(connection, data["message"])
        elif data["action"] == "private_message":
            await mensagem_privada(connection, data['message'], data['receiver'])

start_server = websockets.serve(main, "localhost", 4444)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()