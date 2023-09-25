import pandas as pd
import datetime

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

def contratos(rcs, PMaster, Padi, n=10,):
    """
    Pegar os 10 maiores contratos de cada órgão e ordená-los do maior para o menor considerando a soma do valor empenhado líquido no ano de um contrato com um mesmo número Nº GRPFOR.\n
    OBS: - Caso o contrato possua aditivos, sua data final será substituida pela data final do último aditivo. \n
    rcs = Relatório Contrato Sintético, é o caminho onde a planilha gerada pelo código será armazenada\n
    PMaster = É variável onde armazenamos a informação do Relatório Contrato Sintético.\n
    Padi = É a variável onde armazenamos a informação do Relatório dos Aditivos atualizados.\n
    """
    verifica = verificar(rcs, ['Coluna1', 'Coluna2'], 'Nome do Arquivo')
    if verifica is not True:
        return verifica  # Retorna mensagem de erro se a verificação falhar

    '''Variáveis'''
    PMaster['Cont. Inst.'] = PMaster['Cont. Inst.'].astype(str)
    PMaster['Exercício'] = PMaster['Exercício'].astype(str)
    PMaster['Contrato_Inst'] = PMaster['Cont. Inst.'].str.cat(PMaster['Exercício'], sep='/')                                                                          
    
    '''# Vigência'''
    cont = 0 
    for l in PMaster['Últ. Aditivo']: # Ler toda coluna Ulti. Aditivo do dataframe
        if l > 0: # Verificar se existe aditivos
            PMaster.iloc[cont,[10]] = PMaster.iloc[cont,[13]] # Substituir a data final pela data de termino do aditivo
        cont += 1
    PMaster['Dt. Início'] = PMaster['Dt. Início'].astype(str)
    PMaster['Dt. Fim'] = PMaster['Dt. Fim'].astype(str)
    PMaster['Vigência'] = PMaster['Dt. Início'].str.cat(PMaster['Dt. Fim'], sep='----')
    uo = PMaster['Sigla'].unique() 
    if len(uo) > 1:
       uo = str(input(f'Esolha a U.O\n{uo}')).strip().upper()
       PMaster = PMaster.loc[PMaster['Sigla'] == uo]
    
    '''Valor Contrato Atualizado'''
    Padi['Valor'] = Padi['Valor'].apply(lambda x: float(x.replace(".", "").replace(",",".")) if isinstance(x, str) else x)
    Padi['Nº GRPFOR'] = Padi['Nº Contrato'].str.split('/', expand=True)[0].astype(int)
    PMaster.rename(columns={'Und. Orc.':'U.O.'}, inplace=True)
    PMaster = PMaster.merge(Padi, on=['Nº GRPFOR', 'U.O.'], how='left')
    PMaster['Valor'] = PMaster['Valor'].fillna(0)
    PMaster['Vlr. Contrato Atualizado'] = PMaster['Vlr. Contrato'] + PMaster['Vlr. Adit. Acréscimo'] - PMaster['Vlr. Adit. Redução']- PMaster['Valor']
 
    '''Empenhado no ano'''
    ano = datetime.date.today().year - 1 #SELECIONA O ANO ATUAL MENOS 1
    empenhado = PMaster.loc[(PMaster['Dt. Emp.'].dt.year == ano) & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] != 6)] # Filtra o DT.EMP para achar apenas os contratos do orgão de 2022 e os valores que sejam diferentes de ANULADO'
    parcelas_relacionadas = PMaster.loc[(PMaster['Dt. Emp.'].dt.year == ano) & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] != 6), ['Nº GRPFOR', 'Valor Parcela']] # Seleciona apenas as colunas Nº GRPFOR e VALOR PARCELA que atendem às condições estabelecidas
    soma_por_grpfor = parcelas_relacionadas.groupby('Nº GRPFOR')['Valor Parcela'].sum().reset_index() # Agrupa e soma os valores repetidos
    empenhado_no_ano = soma_por_grpfor['Valor Parcela'].sum() 
    
    '''Empenhado ATÉ o ano'''
    empenhado_AA = PMaster.loc[(PMaster['Dt. Emp.'].dt.year <= ano) & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] != 6)] #Filtra o DT.EMP para achar apenas os contratos do orgão de até 2022 e os valores que sejam diferentes de ANULADO
    parcelas_relacionadas_AA = PMaster.loc[(PMaster['Dt. Emp.'].dt.year <= ano) & (PMaster['Valor Parcela'] != 'Anulada') & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] != 6), ['Nº GRPFOR', 'Valor Parcela']] #Seleciona apenas as colunas Nº GRPFOR e VALOR PARCELA que atendem às condições estabelecidas
    soma_por_grpfor_AA = parcelas_relacionadas_AA.groupby('Nº GRPFOR')['Valor Parcela'].sum().reset_index() # Agrupa e soma os valores repetidos

    '''União de informações'''
    infos = PMaster[['Nº GRPFOR', 'Contrato_Inst','   Credor', 'Descrição Assunto', 'Vigência', 'Vlr. Contrato Atualizado']].drop_duplicates(subset= ['Nº GRPFOR'])# Remoção de valores duplicados
    empenhados = pd.merge(soma_por_grpfor, soma_por_grpfor_AA, on="Nº GRPFOR")# União de DataFrames
    result = pd.merge(infos, empenhados, how='inner', on='Nº GRPFOR').sort_values(by='Valor Parcela_x', ascending=False) # Ordena pelo Empenhado no ano do maior para o menor
    
    '''Resultado'''
    result['Execução'] = round((result['Valor Parcela_y'] / result['Vlr. Contrato Atualizado']) * 100, 2) # Cálculo da Execução
    result.rename(columns={'Contrato_Inst':'Nº Contrato','Valor Parcela_y': 'Empenhado até o ano', 'Valor Parcela_x': 'Empenhado no ano', '   Credor': 'Contratado', 'Descrição Assunto': 'Objeto'}, inplace= True) #Renomeação de colunas
    result = result[['Nº GRPFOR','Nº Contrato','Contratado', 'Objeto', 'Vigência', 'Vlr. Contrato Atualizado', 'Empenhado até o ano', 'Execução', 'Empenhado no ano']].head(n)
    if result.empty:
        return (f'{uo} não possui contratos de gestão.')
    else:
        result.to_excel('Contratos de Gestão-CGM.xlsx')
        #result.to_excel(f'{dir(rcs)} - Contratos de Gestão.xlsx',index=False)
        return result


def dea(arquivo):
    '''
    Gera um filtro que pega os valores com DEA e os valores sem DEA e os soma.
    O cálculo da execução de DEA é a divisão da soma de DEA pelo valor total.\n
    OBS: Para saber se um contrato tem DEA, a coluna 'Despes' da Planilha armazenada na variável arquivo tem que terminar com 92.\n
    arquivo = Relatorio de Destaques e Empenhos Analíticos\n
    '''
    verifica = verificar(arquivo, ['Despes', 'Vlr. Emp. Líquido'], 'Relatório de Destaques e Empenhos Analítico', header= 3)
    if verifica is not True:
        return verifica  # Retorna mensagem de erro se a verificação falhar

    try:
        P1 = pd.read_excel(arquivo, header=3)
        colunas_obrigatorias = ['Despes', 'Vlr. Emp. Líquido']
        colunas_arquivo = P1.columns.tolist()
        nome_do_arquivo='Relatório de Destaques e Empenhos Analítico'
        
        for coluna in colunas_obrigatorias:
            if coluna not in colunas_arquivo:
                return f'Arquivo errado errado, por favor importe o {nome_do_arquivo} '
                break

        mask = P1['Despes'].astype(str).str.endswith('92')
        soma_dea = P1.loc[mask, 'Vlr. Emp. Líquido'].sum()
        soma_sem_dea = P1.loc[~mask, 'Vlr. Emp. Líquido'].sum()
        valor_total = soma_dea + soma_sem_dea
        execucao_dea = round((soma_dea / valor_total) * 100, 2)
        despezas_de_execicios_anteriores = pd.DataFrame([soma_dea, valor_total, execucao_dea], index=['Valor empenhado com DEA', 'Valor total empenhado', 'Índice de Execução de DEA'])
        return despezas_de_execicios_anteriores.to_json(orient='columns')
    except Exception as e:
        return {"error": f"Erro na função dea: {str(e)}"}, None


def gestão(rcs, PMaster, Padi, n=10):
    '''
    Utiliza-se o mesmo algoritmo do módulo de contratos. Após o cálculo, se não houver Cod. Assu = 6, não há contratos de gestão.\n
    rcs = Relatório Contrato Sintético, é o caminho onde a planilha gerada pelo código será armazenada\n
    PMaster = É variável onde armazenamos a informação do Relatório Contrato Sintético.\n
    Padi = É a variável onde armazenamos a informação do Relatório dos Aditivos atualizados.\n
    '''  
    
    '''Variáveis'''
    PMaster['Cont. Inst.'] = PMaster['Cont. Inst.'].astype(str)
    PMaster['Exercício'] = PMaster['Exercício'].astype(str)
    PMaster['Contrato_Inst'] = PMaster['Cont. Inst.'].str.cat(PMaster['Exercício'], sep='/')                                                                          
    
    '''# Vigência'''
    cont = 0 
    for l in PMaster['Últ. Aditivo']: # Ler toda coluna Ulti. Aditivo do dataframe
        if l > 0: # Verificar se existe aditivos
            PMaster.iloc[cont,[10]] = PMaster.iloc[cont,[13]] # Substituir a data final pela data de termino do aditivo
        cont += 1
    PMaster['Dt. Início'] = PMaster['Dt. Início'].astype(str)
    PMaster['Dt. Fim'] = PMaster['Dt. Fim'].astype(str)
    PMaster['Vigência'] = PMaster['Dt. Início'].str.cat(PMaster['Dt. Fim'], sep='----')
    uo = PMaster['Sigla'].unique() 
    if len(uo) > 1:
       uo = str(input(f'Esolha a U.O\n{uo}')).strip().upper()
       PMaster = PMaster.loc[PMaster['Sigla'] == uo]
    
    '''Valor Contrato Atualizado'''
    Padi['Valor'] = Padi['Valor'].apply(lambda x: float(x.replace(".", "").replace(",",".")) if isinstance(x, str) else x)
    Padi['Nº GRPFOR'] = Padi['Nº Contrato'].str.split('/', expand=True)[0].astype(int)
    PMaster.rename(columns={'Und. Orc.':'U.O.'}, inplace=True)
    PMaster = PMaster.merge(Padi, on=['Nº GRPFOR', 'U.O.'], how='left')
    PMaster['Valor'] = PMaster['Valor'].fillna(0)
    PMaster['Vlr. Contrato Atualizado'] = PMaster['Vlr. Contrato'] + PMaster['Vlr. Adit. Acréscimo'] - PMaster['Vlr. Adit. Redução']- PMaster['Valor']
 
    
    '''Empenhado no ano'''
    ano = datetime.date.today().year - 1 #SELECIONA O ANO ATUAL MENOS 1
    empenhado = PMaster.loc[(PMaster['Dt. Emp.'].dt.year == ano) & (PMaster['Situação.1'] != 'Anulada') & PMaster['Cod. Assu.'] == 6] # Filtra o DT.EMP para achar apenas os contratos do orgão de 2022 e os valores que sejam diferentes de ANULADO'
    parcelas_relacionadas = PMaster.loc[(PMaster['Dt. Emp.'].dt.year == ano) & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] == 6), ['Nº GRPFOR', 'Valor Parcela']] # Seleciona apenas as colunas Nº GRPFOR e VALOR PARCELA que atendem às condições estabelecidas
    soma_por_grpfor = parcelas_relacionadas.groupby('Nº GRPFOR')['Valor Parcela'].sum().reset_index() # Agrupa e soma os valores repetidos
    empenhado_no_ano = soma_por_grpfor['Valor Parcela'].sum() 
    
    '''Empenhado ATÉ o ano'''
    empenhado_AA = PMaster.loc[(PMaster['Dt. Emp.'].dt.year <= ano) & (PMaster['Situação.1'] != 'Anulada') & PMaster['Cod. Assu.'] == 6] #Filtra o DT.EMP para achar apenas os contratos do orgão de até 2022 e os valores que sejam diferentes de ANULADO
    parcelas_relacionadas_AA = PMaster.loc[(PMaster['Dt. Emp.'].dt.year <= ano) & (PMaster['Valor Parcela'] != 'Anulada') & (PMaster['Situação.1'] != 'Anulada') & (PMaster['Cod. Assu.'] == 6), ['Nº GRPFOR', 'Valor Parcela']] #Seleciona apenas as colunas Nº GRPFOR e VALOR PARCELA que atendem às condições estabelecidas
    soma_por_grpfor_AA = parcelas_relacionadas_AA.groupby('Nº GRPFOR')['Valor Parcela'].sum().reset_index() # Agrupa e soma os valores repetidos

    '''União de informações'''
    infos = PMaster[['Nº GRPFOR', 'Contrato_Inst','   Credor', 'Descrição Assunto', 'Vigência', 'Vlr. Contrato Atualizado']].drop_duplicates(subset= ['Nº GRPFOR'])# Remoção de valores duplicados
    empenhados = pd.merge(soma_por_grpfor, soma_por_grpfor_AA, on="Nº GRPFOR")# União de DataFrames
    result = pd.merge(infos, empenhados, how='inner', on='Nº GRPFOR').sort_values(by='Valor Parcela_x', ascending=False) # Ordena pelo Empenhado no ano do maior para o menor
    
    '''Resultado'''
    result['Execução'] = round((result['Valor Parcela_y'] / result['Vlr. Contrato Atualizado']) * 100, 2) # Cálculo da Execução
    result.rename(columns={'Contrato_Inst':'Nº Contrato','Valor Parcela_y': 'Empenhado até o ano', 'Valor Parcela_x': 'Empenhado no ano', '   Credor': 'Contratado', 'Descrição Assunto': 'Objeto'}, inplace= True) #Renomeação de colunas
    result = result[['Nº GRPFOR','Nº Contrato','Contratado', 'Objeto', 'Vigência', 'Vlr. Contrato Atualizado', 'Empenhado até o ano', 'Execução', 'Empenhado no ano']].head(n)
    if result.empty:
        return (f'{uo} não possui contratos de gestão.')
    else:
        result.to_excel('Contratos de Gestão-CGM.xlsx')
        #result.to_excel(f'{dir(rcs)} - Contratos de Gestão.xlsx',index=False)
        return result


def despezas(arquivo):
    '''
    Despesas por programa e comparação com o contrato.\n
    Utilizando a planilha P4 para o cálculo do percentual do que foi empenhado no mês com o saldo da dotação atual.\n
    arquivo = Relatório Acompanhamento e Execução Orçamentaria\n
    '''
    verifica = verificar(arquivo, ['Descrição do Programa', 'Sd Dot.Atual', 'Emp. No Mês', 'Liq. No Mês'], 'Relatório Acompanhamento e Execução Orçamentaria', header=1)
    if verifica is not True:
        return verifica  # Retorna mensagem de erro se a verificação falhar

    try: 
        P4 = pd.read_excel(arquivo, header=1)
        TabDespesadf = P4.groupby(['Descrição do Programa'], as_index=False)[['Sd Dot.Atual', 'Emp. No Mês', 'Liq. No Mês']].sum()
        TabDespesadf['Execução'] = round((TabDespesadf['Emp. No Mês']/TabDespesadf['Sd Dot.Atual']) * 100, 2)
        TabDespesadf.rename(columns={'Descrição do Programa': 'Programa', 'Emp. No Mês': 'Empenhado No Ano', 'Liq. No Mês': 'Liquidado No Ano'}, inplace = True)
        #TabDespesadf.to_excel(f'{dir(rdesp)}Despesas.xlsx', index=False)
        #TabDespesadf.to_excel('Despesas-CGM.xlsx')
        return TabDespesadf.to_json(orient='columns')
    except Exception as e:
         return f"Erro na função despezas: {str(e)}", 400