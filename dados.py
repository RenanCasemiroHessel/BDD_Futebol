import random
from faker import Faker
from datetime import date,timedelta  # usado para anotar datas dos jogos
import psycopg2
from dotenv import load_dotenv
import os

fake = Faker('pt_BR')
random.seed()

# Load environment variables from .env
load_dotenv('info.env')

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    cursor.execute('truncate table arbitro restart identity cascade;')
    cursor.execute('truncate table campeonato restart identity cascade;')
    cursor.execute('truncate table joga restart identity cascade;')
    cursor.execute('truncate table jogador restart identity cascade;')
    cursor.execute('truncate table participa restart identity cascade;')
    cursor.execute('truncate table partida restart identity cascade;')
    cursor.execute('truncate table tabela restart identity cascade;')
    cursor.execute('truncate table time restart identity cascade;')

    # Estrutura 
    NUM_TIMES = 20  
    NUM_RODADAS = 38
    NUM_JOGADORES_POR_TIME = 11
    NUM_ARBITROS = 10 #mínimo possível pois cada rodada tem 10 jogos


    posicoes = [
        'Goleiro',
        'Zagueiro', 'Zagueiro',
        'Lateral', 'Lateral',
        'Volante', 'Volante', 'Volante',
        'Meia',
        'Atacante', 'Atacante'
    ]
    nacionalidades = ["Brasileiro","Argentino","Paraguaio","Holandes"]
    times = [
        ["1", "Atlético Mineiro", "Belo Horizonte (MG)", "Arena MRV"],
        ["2", "Bahia", "Salvador (BA)", "Arena Fonte Nova"],
        ["3", "Botafogo", "Rio de Janeiro (RJ)", "Estádio Nilton Santos"],
        ["4", "Ceará", "Fortaleza (CE)", "Arena Castelão"],
        ["5", "Corinthians", "São Paulo (SP)", "Neo Química Arena"],
        ["6", "Cruzeiro", "Belo Horizonte (MG)", "Mineirão"],
        ["7", "Flamengo", "Rio de Janeiro (RJ)", "Maracanã"],
        ["8", "Fluminense", "Rio de Janeiro (RJ)", "Maracanã"],
        ["9", "Fortaleza", "Fortaleza (CE)", "Arena Castelão"],
        ["10", "Grêmio", "Porto Alegre (RS)", "Arena do Grêmio"],
        ["11", "Internacional", "Porto Alegre (RS)", "Beira-Rio"],
        ["12", "Juventude", "Caxias do Sul (RS)", "Alfredo Jaconi"],
        ["13", "Mirassol", "Mirassol (SP)", "Estádio Campos Maia"],
        ["14", "Palmeiras", "São Paulo (SP)", "Allianz Parque"],
        ["15", "Red Bull Bragantino", "Bragança Paulista (SP)", "Nabi Abi Chedid"],
        ["16", "Santos", "Santos (SP)", "Vila Belmiro"],
        ["17", "São Paulo", "São Paulo (SP)", "MorumBIS"],
        ["18", "Sport Recife", "Recife (PE)", "Ilha do Retiro"],
        ["19", "Vasco da Gama", "Rio de Janeiro (RJ)", "São Januário"],
        ["20", "Vitória", "Salvador (BA)", "Barradão"]
    ]


    jogadores = []  
    arbitros = []
    partidas = {}

    # gerando jogadores
    for x in times:
        for i in range(NUM_JOGADORES_POR_TIME):
            nome =  fake.name_male()
            idade = random.randint(18, 38)
            nacionalidade = random.choice(nacionalidades)
            time = x[1]
            posicao = posicoes[i]

            #adicionando no dicionário
            jogador= {
                'nome' : nome,
                "idade": idade,
                "nacionalidade": nacionalidade,
                "time": time,
                "posição": posicao
            }
            jogadores.append(jogador)

    # gerando árbitros
    for i in range(NUM_ARBITROS):
        x = i%2
        id = i+1,
        M = fake.name_male(),
        F = fake.name_female(),
        if(x == 0):
            nome = M[0]
            sexo = "Masculino"
        else: 
            nome = F[0]
            sexo = "Feminino"

        arbitro = {
            'id': id,
            'nome' : nome,
            'categoria': "CBF",
            'sexo': sexo
        }
        arbitros.append(arbitro)

    # Campeonato
    campeonato = [152,"Campeonato Brasileiro",2025]

    # gerando partidas (rodada a rodada) e datas 

    datas = []
    data_inicio = date(2025, 3, 29)
    for rodada in range(38):
        sabado = data_inicio + timedelta(weeks=rodada)
        domingo = sabado + timedelta(days=1)
        sabado_form = sabado.strftime("%d/%m/%y")
        domingo_form = domingo.strftime("%d/%m/%y")
        for _ in range(5):
            datas.append(sabado_form)
        for _ in range(5):
            datas.append(domingo_form)

    partidas = []
    partida_id = 1
    times_ids = [time[0] for time in times]
    print(times_ids)
    confrontos_ida = []
    confrontos_volta = []

    for i in range(len(times_ids)):
        for j in range(i+1, len(times_ids)):
            time1 = times_ids[i]
            time2 = times_ids[j]
            confrontos_ida.append((time1, time2))  
            confrontos_volta.append((time2, time1))
    confrontos = confrontos_ida + confrontos_volta

    for rodada, confronto in enumerate(confrontos):
        time1_id, time2_id = confronto 
        arbitro = random.choice(arbitros)
        partida = {
            'id': partida_id,
            'campeonato_id': campeonato[0],
            'rodada': (rodada // 10) + 1, 
            'time1_id': time1_id,
            'time2_id': time2_id,
            'data': datas[rodada],  
            'placar_time1': random.randint(0, 5),
            'placar_time2': random.randint(0, 5),
            'arbitro_id': arbitro['id'][0]
            }
        partidas.append(partida)
        partida_id += 1


    # Criar tabela de classificação
    classificacao = {}
    for time in times:
        classificacao[time[0]] = {
            'pontos': 0,
            'vitorias': 0,
            'empates': 0,
            'derrotas': 0,
            'gols_pro': 0,
            'gols_contra': 0
        }

    for partida in partidas:
        time1 = partida['time1_id']
        time2 = partida['time2_id']
        g1 = partida['placar_time1']
        g2 = partida['placar_time2']
        classificacao[time1]['gols_pro'] += g1
        classificacao[time1]['gols_contra'] += g2
        classificacao[time2]['gols_pro'] += g2
        classificacao[time2]['gols_contra'] += g1
        
        #fazendos os pontos de vitória, derropa e empate para cada time
        if g1 > g2:
            classificacao[time1]['pontos'] += 3
            classificacao[time1]['vitorias'] += 1
            classificacao[time2]['derrotas'] += 1
        elif g1 < g2:
            classificacao[time2]['pontos'] += 3
            classificacao[time2]['vitorias'] += 1
            classificacao[time1]['derrotas'] += 1
        else:
            classificacao[time1]['pontos'] += 1
            classificacao[time2]['pontos'] += 1
            classificacao[time1]['empates'] += 1
            classificacao[time2]['empates'] += 1

    # Montar classificação final ordenada
    classificacao_final = sorted(classificacao.items(), key=lambda x: (x[1]['pontos'], x[1]['gols_pro'] - x[1]['gols_contra']), reverse=True)

    tabela_final = []
    for time_id, stats in classificacao_final:
        tabela = {
            'campeonato_id': campeonato[0],
            'time_id': time_id,
            'pontos': stats['pontos'],
            'vitorias': stats['vitorias'],
            'empates': stats['empates'],
            'derrotas': stats['derrotas'],
            'gols_pro': stats['gols_pro'],
            'gols_contra': stats['gols_contra'],
            'saldo_gols': stats['gols_pro'] - stats['gols_contra'],
        }
        tabela_final.append(tabela)

    # Agora, imprimimos os INSERTS!

    print("-- INSERT Times")
    for t in range(20):
        cursor.execute(f"INSERT INTO Time (nome, cidade, estadio) VALUES ('{times[t][1]}', '{times[t][2]}', '{times[t][3]}');")

    print("\n-- INSERT Campeonato")
    cursor.execute(f"INSERT INTO Campeonato (id,nome, ano) VALUES ('{campeonato[0]}','{campeonato[1]}', {campeonato[2]});")

    print("\n-- INSERT Jogadores")
    for j in jogadores:
        cursor.execute(f"INSERT INTO Jogador (nome, idade, nacionalidade, time, posicao) VALUES ('{j['nome']}', {j['idade']}, '{j['nacionalidade']}', '{j['time']}', '{j['posição']}');")

    print("\n-- INSERT Árbitros")
    for a in arbitros:
        cursor.execute(f"INSERT INTO Arbitro (nome, categoria, federacao) VALUES ('{a['nome']}', '{a['categoria']}', '{a['sexo']}');")

    print("\n-- INSERT Participação")
    for t in range(20):
        cursor.execute(f"INSERT INTO Participa (campeonato_id, time_id) VALUES ({campeonato[0]}, {times[t][0]});")

    print("\n-- INSERT Partidas")
    for p in partidas:
        cursor.execute(f"INSERT INTO Partida (campeonato_id, rodada, time1_id, time2_id, data, placar_time1, placar_time2) VALUES ({p['campeonato_id']}, {p['rodada']}, {p['time1_id']}, {p['time2_id']}, '{p['data']}', {p['placar_time1']}, {p['placar_time2']});")

    print("\n-- INSERT Árbitros em Partidas (Joga)")
    for p in partidas:
        cursor.execute(f"INSERT INTO Joga (partida_id, arbitro_id) VALUES ({p['id']}, {p['arbitro_id']});")

    print("\n-- INSERT Tabela Final")
    for t in tabela_final:
        cursor.execute(f"INSERT INTO Tabela (campeonato_id, time_id, pontos, vitorias, empates, derrotas, gols_pro, gols_contra, saldo_gols) VALUES ({t['campeonato_id']}, {t['time_id']}, {t['pontos']}, {t['vitorias']}, {t['empates']}, {t['derrotas']}, {t['gols_pro']}, {t['gols_contra']}, {t['saldo_gols']});")


    cursor.execute('commit')
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")


