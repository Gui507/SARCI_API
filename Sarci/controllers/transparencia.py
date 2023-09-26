import pandas as pd

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


def pedidos(rpos, uo = None):
    verifica = verificar(rpos, colunas_obrigatorias=['Nº de Pedidos', 'Nº de pedidos dentro do prazo (20 dias)', 'Nº de pedidos fora do prazo (> 20 dias)', 'Tempo Médio de Resposta do Pedido ', 'Recurso de 1ª Instância', 'Recurso de 2ª Instância', 'Recurso de 3ª Instância'], nome_do_arquivo='Relatório Ranking Simplificado', header=4)
    if verifica is not True:
        return verifica
    
    try:
        df_base = pd.read_excel(rpos, header=4)
        orgao = df_base.loc[df_base['ÓRGÃOS'] == uo]
        orgao['N° de Pedidos Respondidos'] = orgao['Nº de pedidos dentro do prazo (20 dias)'].astype(int) + orgao['Nº de pedidos fora do prazo (> 20 dias)'].astype(int)
        df_final = orgao[['Nº de Pedidos','N° de Pedidos Respondidos','Tempo Médio de Resposta do Pedido ','Recurso de 1ª Instância','Recurso de 2ª Instância','Recurso de 3ª Instância']]
        
        resultado_dict = df_final.to_dict(orient='records')

        # Converta a lista de dicionários em JSON usando jsonify
        return resultado_dict
    except Exception as e:
        return {"error": f"Erro na função pedidos: {str(e)}"}, None

def ranking_assunto(rp, uo = None):
    verifica = verificar(rp, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica

    try:
        df = pd.read_excel(rp, header=4)
        orgao = df.loc[df['Orgão (SIC)'].astype(str).str.startswith(uo) & (df['Situação\n(*)'] == 'R')]
        ranking = orgao['Assunto'].value_counts().reset_index()
        ranking = ranking.rename(columns={'count': 'Quantidade'})
        total = ranking['Quantidade'].sum()
        ranking['% Pedidos'] = (ranking['Quantidade'] / total) * 100
        ranking['% Pedidos'] = ranking['% Pedidos'].map('{:.2f}%'.format)
        #ranking.to_excel(f'{dir(rp)}Ranking Assunto - {uo}.xlsx',index=False)
        ranking.to_excel('Ranking Assunto-CGM.xlsx')
        return ranking
    except Exception as e:
        return {"error": f"Erro na função dea: {str(e)}"}, None
   

def inventario_base(pda):
    verifica = verificar(pda, colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO'], nome_do_arquivo='Relatório de Manifestação')
    if verifica is not True:
        return verifica

    try:    
        import docx
        pd.set_option('display.max_colwidth', None)
        # Abrir o arquivo do Word
        documento = docx.Document(pda)

        # Criar uma lista para armazenar as tabelas
        tabelas = []

        # Variável para armazenar a tabela atual
        tabela_atual = []

        # Percorrer as tabelas do documento
        for tabela in documento.tables:
            # Verificar se é uma nova tabela
            if tabela.rows[0].cells[0].text.strip() != '':
                # Verificar se existe tabela anterior
                if tabela_atual:
                    # Adicionar tabela anterior à lista de tabelas
                    tabelas.append(tabela_atual)

                # Iniciar uma nova tabela
                tabela_atual = []

            # Percorrer as linhas da tabela
            for row in tabela.rows:
                # Criar uma lista para armazenar as células da linha
                celulas = []

                # Percorrer as células da linha e adicionar o texto à lista
                for cell in row.cells:
                    celulas.append(cell.text.replace('\n', ''))

                # Adicionar a lista de células à tabela atual
                tabela_atual.append(celulas)

        # Adicionar última tabela à lista de tabelas
        tabelas.append(tabela_atual)

        # Converter as tabelas em DataFrames
        dataframes = [pd.DataFrame(tabela) for tabela in tabelas]

        # Seleciona os elementos uteis da lista
        df_util = pd.DataFrame(dataframes[0])
        df_util.columns = df_util.iloc[0]

        # Remove a primeira linha do DataFrame
        df_util = df_util.iloc[1:]

        # Resultado
        padroes = ['^Nome', '^Descrição', '^Unidade', '^Periodicidade']
        col_selecionadas = df_util.filter(regex='|'.join(padroes), axis=1)
        #col_selecionadas.to_excel(f'{dir(pda)}Invetário de Base de Dados - IPEM.xlsx')
        col_selecionadas.to_excel('Inventario de base de dados-CGM.xlsx')
        return col_selecionadas
    except Exception as e:
        return {"error": f"Erro na função dea: {str(e)}"}, None
