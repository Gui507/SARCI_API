import pandas as pd

def verificar(arq, colunas_obrigatorias, nome_do_arquivo, c=0):
    try:
        df = pd.read_excel(arq, header=c)
        colunas_arquivo = df.columns.tolist()

        for coluna in colunas_obrigatorias:
            if coluna not in colunas_arquivo:
                return f'Arquivo errado errado, por favor importe o {nome_do_arquivo} '
            else:
                return True
    except Exception as e:
        return False, f"Erro na leitura do arquivo {e}"

def contagem(rmanifest, uo=None):
    try: 
        df = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
        
        if uo:
            uo = uo.upper()  # Transforma o órgão especificado em maiúsculas
            if uo not in df['ÓRGÃO'].str.upper().unique():
                return {"error": f"ÓRGÃO '{uo}' não encontrado nos dados"}
            df = df[df['ÓRGÃO'].str.upper() == uo]

        counts = df['TIPO DE MANIFESTAÇÃO'].value_counts()
        counts = counts.reindex(['Elogio', 'Denúncia', 'Reclamação', 'Solicitação', 'Sugestão']).fillna(0)
        counts = counts.to_frame().transpose()  # Transpor o DataFrame
        return counts.to_json(orient='columns')
    except Exception as e:
        return {"error": f"Erro na função contagem: {str(e)}"}

def total(rmanifest, uo):
    try:
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')

        if uo:
            uo = uo.upper()  # Transforma o órgão especificado em maiúsculas
            if uo not in manifest['ÓRGÃO'].str.upper().unique():
                return {"error": f"ÓRGÃO '{uo}' não encontrado nos dados"}
            total = manifest[manifest['ÓRGÃO'].str.upper() == uo].shape[0]
        else:
            total = manifest.groupby(['ÓRGÃO']).size().to_dict()
        return total
    except Exception as e:
        return {"error": f"Erro na função total: {str(e)}"}

def respondidas(rmanifest, uo):
    try:
        global ano_atual
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
        manifest_respondidas = manifest.dropna(subset=['DATA DE RESPOSTA'])
        # Filtrar as respostas do ano atual
        manifest_respondidas['DATA DE RESPOSTA'] = pd.to_datetime(manifest_respondidas['DATA DE RESPOSTA'], dayfirst=True)
        manifest_respondidas = manifest_respondidas[manifest_respondidas['DATA DE RESPOSTA'].dt.year != ano_atual]
        manifest_por_orgao = manifest_respondidas.groupby('ÓRGÃO').size()
        return manifest_por_orgao[uo]
    except Exception as e:
        return {"error": f"Erro na função respondidas: {str(e)}"}

def tempomedioresp(rmanifest, uo):
    try:
        global ano_atual
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').fillna(0)
        manifest_com_tempo = manifest.dropna(subset=['PERÍODO DE ATENDIMENTO EM DIAS'])
        manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'] = pd.to_numeric(manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'])
        tempo_medio_por_orgao = round(manifest_com_tempo.loc[(manifest["DATA DE RESPOSTA"] != 0) & (manifest["DATA DE RESPOSTA"] != ano_atual) ].groupby('ÓRGÃO')['PERÍODO DE ATENDIMENTO EM DIAS'].mean(), 2)
        return tempo_medio_por_orgao[uo]
    except Exception as e:
        return {"error": f"Erro na função tempomedioresp: {str(e)}"}

def ranking_assunto(rmanifest, uo):
    try:
        df = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').groupby('ÓRGÃO')
        ranking = df['ASSUNTO'].value_counts().reset_index()
        ranking_uo = ranking.loc[ranking['ÓRGÃO'] == uo]
        ranking_uo = ranking_uo.drop(columns=['ÓRGÃO'])
        ranking_uo = ranking_uo.rename(columns={'ASSUNTO': 'Demanda', 'count': 'Quantidade'})
        ranking_uo.to_excel('Ranking por Assunto-CGM0942.xlsx')
        return ranking_uo
    except Exception as e:
        return {"error": f"Erro na função ranking_assunto: {str(e)}"}

