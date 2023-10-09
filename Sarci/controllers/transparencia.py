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


def pedidos(rpos, uo):
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
    verifica = verificar(rp, colunas_obrigatorias=['Orgão (SIC)', 'Situação\n(*)', 'Assunto'], nome_do_arquivo='Relatório de Pedidos', header=4)
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
        #ranking.to_excel('Ranking Assunto-CGM.xlsx')
        ranking = ranking.to_dict(orient='records')
        return ranking
    except Exception as e:
        return {"error": f"Erro na função dea: {str(e)}"}, None
   
# PARAMOS AQUI!!!
''' Esta retornando o seginte erro:
error: No module named exceptions
'''

def inventario_base(pda):
    import docx
    from flask import jsonify
    try:
        # Abre o arquivo do Word fornecido ('pda') usando a biblioteca 'docx'.
        documento = docx.Domunet(pda)

        # Cria uma lista chamada 'tabelas' para armazenar as tabelas encontradas no documento.
        tabelas = []

        # Cria uma lista vazia chamada 'tabela_atual' para armazenar a tabela atualmente processada.
        tabela_atual = []

        # Percorre as tabelas no documento do Word.
        for tabela in documento.tables:
            # Verifica se é uma nova tabela verificando o conteúdo da primeira célula da primeira linha.
            if tabela.rows[0].cells[0].text.strip() != '':
                # Se já tiver uma 'tabela_atual' (ou seja, estamos em uma nova tabela), adiciona a tabela anterior à lista 'tabelas'.
                if tabela_atual:
                    tabelas.append(tabela_atual)

                # Inicia uma nova tabela limpando 'tabela_atual'.
                tabela_atual = []

            # Percorre as linhas da tabela.
            for row in tabela.rows:
                # Cria uma lista chamada 'celulas' para armazenar o texto de cada célula da linha.
                celulas = []

                # Percorre as células da linha e adiciona o texto à lista 'celulas'.
                for cell in row.cells:
                    celulas.append(cell.text.replace('\n', ''))

                # Adiciona a lista de 'celulas' à 'tabela_atual'.
                tabela_atual.append(celulas)

        # Após o loop, adiciona a última 'tabela_atual' à lista 'tabelas'.
        tabelas.append(tabela_atual)

        # Converte as tabelas em DataFrames do Pandas.
        dataframes = [pd.DataFrame(tabela) for tabela in tabelas]

        # Seleciona o primeiro DataFrame (a primeira tabela) da lista.
        df_util = pd.DataFrame(dataframes[0])

        # Define a primeira linha do DataFrame como cabeçalho de coluna.
        df_util.columns = df_util.iloc[0]

        # Remove a primeira linha do DataFrame, pois já foi usada como cabeçalho.
        df_util = df_util.iloc[1:]

        # Define um padrão para as colunas desejadas.
        padroes = ['^Nome', '^Descrição', '^Unidade', '^Periodicidade']

        # Filtra as colunas do DataFrame com base nos padrões.
        col_selecionadas = df_util.filter(regex='|'.join(padroes), axis=1)

        # Converte o DataFrame resultante em um dicionário de registros.
        resultado_json = col_selecionadas.to_dict(orient='records')

        # Retorna o resultado como uma resposta JSON usando a função 'jsonify'.
        return jsonify(resultado_json)

    except Exception as e:
        # Se ocorrer um erro, retorna uma resposta JSON com uma mensagem de erro e um código de status 500 (erro interno do servidor).
        return {"error": f"Erro na função processar_inventario_base: {str(e)}"}, 500