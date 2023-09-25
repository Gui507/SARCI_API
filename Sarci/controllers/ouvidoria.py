import pandas as pd
ano_atual = pd.Timestamp.now().year

def verificar(arq, colunas_obrigatorias, nome_do_arquivo, header=0):
    try:
        df = pd.read_excel(arq, header=header)
        colunas_arquivo = df.columns.tolist()

        for coluna in colunas_obrigatorias:
            if coluna not in colunas_arquivo:
                return f'Arquivo errado errado, por favor importe o {nome_do_arquivo} '
            else:
                return True
    except Exception as e:
        return False, f"Erro na leitura do arquivo {e}"


def total(rmanifest, uo=None):
    verifica = verificar(rmanifest, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica

    try:
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
        if uo:
            uo = uo.upper()  # Transforma o órgão especificado em maiúsculas
            if uo not in manifest['ÓRGÃO'].str.upper().unique():
                return {"error": f"ÓRGÃO '{uo}' não encontrado nos dados"}
            total = manifest[manifest['ÓRGÃO'].str.upper() == uo].shape[0]
            mensagem = {f"Total de manifestações ({uo})": total}
        else:
            total_por_orgao = manifest.groupby(['ÓRGÃO']).size().to_dict()
            mensagem = {"Total de manifestações por orgao": total_por_orgao}
        
        return mensagem
    
    except Exception as e:
        return {"error": f"Erro na função total: {str(e)}"}


    


def contagem(rmanifest, uo=None):
    verifica = verificar(rmanifest, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica
    
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
        
        if uo:
            mensagem = f"Contagem de tipos de manifestações ({uo}):\n"
        else:
            mensagem = "Contagem de tipos de manifestações por órgão:\n"

        for tipo, total in counts.iloc[0].items():
            mensagem += f"{tipo}: {int(total)}\n"

        return {"mensagem": mensagem}
    except Exception as e:
        return {"error": f"Erro na função contagem: {str(e)}"}


def respondidas(rmanifest, uo=None):
    verifica = verificar(rmanifest, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica
    
    try:
        global ano_atual
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
        manifest_respondidas = manifest.dropna(subset=['DATA DE RESPOSTA'])
        manifest_respondidas['DATA DE RESPOSTA'] = pd.to_datetime(manifest_respondidas['DATA DE RESPOSTA'], dayfirst=True)
        manifest_respondidas = manifest_respondidas[manifest_respondidas['DATA DE RESPOSTA'].dt.year != ano_atual]
        manifest_por_orgao = manifest_respondidas.groupby('ÓRGÃO').size()
        
        if uo:
            mensagem = f"Total de manifestações respondidas ({uo}): {manifest_por_orgao.get(uo, 0)}"
        else:
            mensagem = "Total de manifestações respondidas por órgão:\n"
            for orgao, total in manifest_por_orgao.items():
                mensagem += f"{orgao}: {total}\n"
        
        return {"mensagem": mensagem}
    
    except Exception as e:
        return {"error": f"Erro na função respondidas: {str(e)}"}


def tempomedioresp(rmanifest, uo=None):
    verifica = verificar(rmanifest, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica
    
    try:
        global ano_atual
        manifest = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO').fillna(0)
        manifest_com_tempo = manifest.dropna(subset=['PERÍODO DE ATENDIMENTO EM DIAS'])
        manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'] = pd.to_numeric(manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'])
        tempo_medio_por_orgao = round(manifest_com_tempo.loc[(manifest["DATA DE RESPOSTA"] != 0) & (manifest["DATA DE RESPOSTA"] != ano_atual)].groupby('ÓRGÃO')['PERÍODO DE ATENDIMENTO EM DIAS'].mean(), 2)
        
        if uo:
            mensagem = f"Tempo médio de resposta ({uo}): {tempo_medio_por_orgao.get(uo, 0)} dias"
        else:
            mensagem = "Tempo médio de resposta por órgão:\n"
            for orgao, tempo_medio in tempo_medio_por_orgao.items():
                mensagem += f"{orgao}: {tempo_medio} dias\n"
        
        return {"mensagem": mensagem}
    
    except Exception as e:
        return {"error": f"Erro na função tempomedioresp: {str(e)}"}

def ranking_assunto(rmanifest, uo=None):
    verifica = verificar(rmanifest, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica
    
    try:
        df = pd.read_excel(rmanifest).drop_duplicates('PROTOCOLO')
        ranking = df['ASSUNTO'].value_counts().reset_index()
        ranking = ranking.rename(columns={'index': 'Demanda', 'ASSUNTO': 'Quantidade'})
        
        if uo:
            ranking_orgao = df[df['ÓRGÃO'] == uo]['ASSUNTO'].value_counts().reset_index()
            ranking_orgao = ranking_orgao.rename(columns={'index': 'Demanda', 'ASSUNTO': 'Quantidade'})
            
            return {
                "Ranking de assuntos mais demandados": ranking.to_dict(orient="records"),
                "Ranking de assuntos mais demandados para o órgão especificado": ranking_orgao.to_dict(orient="records")
            }
        else:
            return {"Ranking de assuntos mais demandados": ranking.to_dict(orient="records")}
    
    except Exception as e:
        return {"error": f"Erro na função ranking_assunto: {str(e)}"}


