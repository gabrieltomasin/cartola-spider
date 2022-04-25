import requests
import pandas as pd

#Requests para obter número de rodadas e mercado
n_rodadas = requests.get("https://api.cartolafc.globo.com/mercado/status")
n_rodadas = n_rodadas.json()
n_rodadas = n_rodadas["rodada_atual"]-1
mercado = requests.get("https://api.cartolafc.globo.com/atletas/mercado")
mercado = mercado.json()

#Definindo função de substituição de id de time e de posição pelos nomes correspondentes
#Definindo mappers (serão utilizados para substituir ids pelos nomes de clubes e posicoes)
clube_mapper = {int(key): mercado['clubes'][key]['nome'] for key in mercado['clubes']}
posicao_mapper = {int(key): mercado['posicoes'][key]['abreviacao'] for key in mercado['posicoes']}
def substitui_ids(dados, clube_mapper = clube_mapper, posicao_mapper = posicao_mapper):
    dados['clube_id'] = dados['clube_id'].map(clube_mapper)
    dados['posicao_id'] = dados['posicao_id'].map(posicao_mapper)
    dados.rename(columns={'clube_id': 'clube', 'posicao_id': 'posicao'}, inplace=True)
    return dados

#Definindo função de dividir a coluna 'scouts' em uma coluna para cada scout
def divide_scouts(dados):
    dados = pd.concat([dados.drop(['scout'],axis=1),dados['scout'].apply(pd.Series)],axis=1)
    return dados

#Iterando cada rodada
for i in range(n_rodadas):
    dados_rodada = requests.get('https://api.cartolafc.globo.com/atletas/pontuados/%s' %str(i+1))
    dados_rodada = dados_rodada.json()
    #Gerando DataFrame e arquivos .csv
    df = pd.DataFrame.from_dict(dados_rodada["atletas"], orient='index')
    df = divide_scouts(df)
    del df["foto"] #Deletando urls das fotos dos jogadores
    df = substitui_ids(df)
    df.to_csv('rodada{}.csv'.format(str(i+1)))

#Gerando tabela geral (Todas as rodadas)
df = pd.DataFrame(mercado['atletas'])
df = divide_scouts(df)
del df["foto"]
df = substitui_ids(df)
df.to_csv('geral.csv')
