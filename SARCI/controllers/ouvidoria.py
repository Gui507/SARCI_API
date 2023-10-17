import pandas as pd
ano_atual = pd.Timestamp.now().year
def dir(arq):
    "Armazena o diretório do arquivo"
    d = arq[0].rfind('/'or '\\')
    return (arq[:d+1])


def contagem(rmanifest, uo):
    df = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').groupby('ÓRGÃO')
    counts = df['TIPO DE MANIFESTAÇÃO'].value_counts()
    counts_uo = counts[uo]
    counts_uo = counts_uo.to_frame().transpose()  # Transpor o DataFrame
    columns_order = ['Elogio', 'Denúncia', 'Reclamação', 'Solicitação', 'Sugestão']
    counts_uo = counts_uo.reindex(columns_order, axis=1)  # Reordenar as colunas
    return counts_uo


def total(rmanifest, uo):
    manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
    total = manifest.groupby(['ÓRGÃO']).size()
    return total[uo]


def respondidas(rmanifest, uo):
    global ano_atual
    manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
    manifest_respondidas = manifest.dropna(subset=['DATA DE RESPOSTA'])

    # Filtrar as respostas do ano atual
    manifest_respondidas['DATA DE RESPOSTA'] = pd.to_datetime(manifest_respondidas['DATA DE RESPOSTA'], dayfirst=True)
    manifest_respondidas = manifest_respondidas[manifest_respondidas['DATA DE RESPOSTA'].dt.year != ano_atual]
    manifest_por_orgao = manifest_respondidas.groupby('ÓRGÃO').size()
    return manifest_por_orgao[uo]

def tempomedioresp(rmanifest, uo):
    global ano_atual
    manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').fillna(0)
    manifest_com_tempo = manifest.dropna(subset=['PERÍODO DE ATENDIMENTO EM DIAS'])
    manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'] = pd.to_numeric(manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'])
    tempo_medio_por_orgao = round(manifest_com_tempo.loc[(manifest["DATA DE RESPOSTA"] != 0) & (manifest["DATA DE RESPOSTA"] != ano_atual) ].groupby('ÓRGÃO')['PERÍODO DE ATENDIMENTO EM DIAS'].mean(), 2)
    return tempo_medio_por_orgao[uo]

def ranking_assunto(rmanifest,uo):
    df = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').groupby('ÓRGÃO')
    ranking = df['ASSUNTO'].value_counts().reset_index()
    ranking_uo = ranking.loc[ranking['ÓRGÃO'] == uo]
    ranking_uo = ranking_uo.drop(columns=['ÓRGÃO'])
    ranking_uo = ranking_uo.rename(columns={'ASSUNTO': 'Demanda', 'count': 'Quantidade'})
    #ranking_uo.to_excel(f'{dir(rmanifest)}Ranking por Assunto - {uo}.xlsx',index=False)
    ranking_uo.to_excel('Ranking por Assunto-CGM0942.xlsx')
    return ranking_uo