from Sarci.config import app
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
import pandas as pd
from datetime import timedelta
# import psycopg2
# import dotenv
# import os

# dotenv.load_dotenv()
'''
# TESTE NA CGM (COM BANCO DE DADOS)
def conectar_bd():
    return psycopg2.connect(host=os.getenv('host'), database=os.getenv('database'), port=os.getenv('port'), user=os.getenv('user'), password=os.getenv('password'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
    else:
        data = request.args
        username = data.get('username')
        password = data.get('password')
        # concetar ao banco de dados
        conexao = conectar_bd()
        
        # Cria um cursor para executar comandos SQL
        cursor = conexao.cursor()
        
        # Executa o comando SQL
        cursor.execute('SELECT * FROM usuarios WHERE username = %s AND senha = %s',(username, password))
        resultado = cursor.fetchone()

        # Fecha o cursor e a conexão
        cursor.close()
        conexao.close()

        # Validação
        if resultado is not None:
            access_token = create_access_token(identity=resultado[0], expires_delta=timedelta(minutes=20))
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'message': 'Invalid credentials'})
'''

# TESTE EM CASA (SEM BANCO DE DADOS)
db =[
{
    'id': '1', 
    'user': 'soyEldvd', 
    'username': 'Calixto', 
    'password': '123'
},
{
    'id': '2', 
    'user': 'Guilherme', 
    'username': 'Gui507', 
    'password': '12345'
}
]


@app.route('/', methods = ['GET'])
def print():
    return 'TESTE'


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
    else:
        data = request.args
        username = data.get('username')
        password = data.get('password')
        matching_user = None
        for user in db:
            if user['username'] == username and user['password'] == password:
                matching_user = user
                break

        if matching_user:
            access_token = create_access_token(identity=matching_user['id'], expires_delta=timedelta(minutes=20))
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'message': 'Invalid credentials'})


@app.route('/dea', methods = ['POST'])
@jwt_required()
def dea():
    # Verificar se o arquivo foi enviado
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    # Obter o arquivo enviado
    arquivo = request.files['file']

    # Verificar se o arquivo está vazio
    if arquivo.filename == '':
        return 'O arquivo está vazio', 400
    
    # Verificar a extensão do arquivo
    extensoes_permitidas = ['xlsx', 'csv', 'xls']  # Exemplo de lista de extensões permitidas
    extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
    if extensao_arquivo not in extensoes_permitidas:
        extensoes_permitidas_str = ', '.join(extensoes_permitidas)
        return f'Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}', 400
    

    # leitura do arquivo
    if extensao_arquivo == 'xlsx' or extensao_arquivo == 'xls' or extensao_arquivo == 'csv': 
        try:
            P1 = pd.read_excel(arquivo, header=3)
        except Exception as e:
            return f"Erro na leitura do arquivo {e}", 400

    

    # Verifica se as colunas existem no arquivo
    colunas_arquivo = P1.columns.tolist()
    colunas_obrigatorias = ['Despes', 'Vlr. Emp. Líquido']
    for coluna in colunas_obrigatorias:
        if coluna not in colunas_arquivo:
            return f'Arquivo errado, por favor importe o relaório de empenho e destaques analiticos', 400
        else:
            # Restante do seu código para processar o arquivo
            mask = P1['Despes'].astype(str).str.endswith('92')
            soma_dea = P1.loc[mask, 'Vlr. Emp. Líquido'].sum()
            soma_sem_dea = P1.loc[~mask, 'Vlr. Emp. Líquido'].sum()
            valor_total = soma_dea + soma_sem_dea
            execucao_dea = round((soma_dea / valor_total) * 100, 2)
            despezas_de_execicios_anteriores = pd.DataFrame([soma_dea,valor_total,execucao_dea],index=['Valor empenhado com DEA', 'Valor total empenhado', 'Índice de Execução de DEA'])
            return despezas_de_execicios_anteriores.to_json(orient='columns')


@app.route('/despesas', methods = ['POST'])
@jwt_required()
def despesas():
    # Verificar se o arquivo foi enviado
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400

    # Obter o arquivo enviado
    arquivo = request.files['file']

    # Verificar se o arquivo está vazio
    if arquivo.filename == '':
        return 'O arquivo está vazio', 400
    
    # Verificar a extensão do arquivo
    extensoes_permitidas = ['xlsx', 'csv', 'xls']  # Exemplo de lista de extensões permitidas
    extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
    if extensao_arquivo not in extensoes_permitidas:
        extensoes_permitidas_str = ', '.join(extensoes_permitidas)
        return f'Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}', 400
    
    # leitura do arquivo
    if extensao_arquivo == 'xlsx' or extensao_arquivo == 'xls' or extensao_arquivo == 'csv': 
        try:
            P4 = pd.read_excel(arquivo, header=1)
        except Exception as e:
            return f"Erro na leitura do arquivo {e}", 400

    colunas_arquivo = P4.columns.tolist()
    colunas_obrigatorias = ['Descrição do Programa', 'Progr.', 'Emp. No Mês', 'Sd Dot.Atual', 'Emp. No Mês', 'Liq. No Mês']

    for coluna in colunas_obrigatorias:
        if coluna not in colunas_arquivo:
            return f'Arquivo errado, por favor importar o relatorio de despesas', 400
        else:
            TabDespesadf = P4.groupby(['Descrição do Programa'], as_index=False)[['Sd Dot.Atual', 'Emp. No Mês', 'Liq. No Mês']].sum()
            TabDespesadf['Execução'] = round((TabDespesadf['Emp. No Mês'] / TabDespesadf['Sd Dot.Atual']) * 100, 2)
            TabDespesadf.rename(columns={'Descrição do Programa': 'Programa', 'Emp. No Mês': 'Empenhado No Ano', 'Liq. No Mês': 'Liquidado No Ano'}, inplace = True)
            # TabDespesadf.to_excel(f'{dir(rdesp)}Despesas.xlsx', index=False)
            # TabDespesadf.to_excel('Despesas-CGM.xlsx')
            return TabDespesadf.to_json(orient='columns')
        

@app.route('/ouvidoria/total-de-manifestacoes', methods=['POST'])
@jwt_required()
def total_manifest():
   try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return 'Nenhum arquivo enviado', 400

        # Obter o arquivo enviado
        arquivo = request.files['file']

        # Verificar se o arquivo está vazio
        if arquivo.filename == '':
            return 'O arquivo está vazio', 400

        # Verificar a extensão do arquivo
        extensoes_permitidas = ['xlsx', 'csv', 'xls']  # Exemplo de lista de extensões permitidas
        extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao_arquivo not in extensoes_permitidas:
            extensoes_permitidas_str = ', '.join(extensoes_permitidas)
            return f'Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}', 400

        # Leitura do arquivo
        if extensao_arquivo in ['xlsx', 'xls', 'csv']:
            try:
                rmanifest = pd.read_excel(arquivo)
            except Exception as e:
                return f"Erro na leitura do arquivo {e}", 400

            colunas_arquivo = rmanifest.columns.tolist()
            colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO']

            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return f'Arquivo errado, por favor importar o relatório de manifestações', 400

            # Obter o órgão especificado pelo usuário, se fornecido
            orgao_desejado = request.form.get('orgao')
            
            # Remover protocolos duplicados
            rmanifest.drop_duplicates(subset=['PROTOCOLO'], inplace=True)

            if orgao_desejado:
                orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                manifestacoes_orgao = rmanifest[rmanifest['ÓRGÃO'].str.upper() == orgao_desejado]

                # Calcular o total de manifestações para o órgão especificado
                total_manifestacoes = len(manifestacoes_orgao)

                return f'Total de manifestações para o órgão {orgao_desejado}: {total_manifestacoes}', 200
            else:
                # Se o órgão não foi especificado, calcular o total de manifestações para todos os órgãos
                total_manifestacoes = rmanifest.groupby(['ÓRGÃO']).size()

                return f'Total de manifestações de todos os órgãos: {total_manifestacoes}', 200
   except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ouvidoria/total-tipos', methods=['POST'])
@jwt_required()
def contagem():
    try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        # Obter o arquivo enviado
        arquivo = request.files['file']

        # Verificar se o arquivo está vazio
        if arquivo.filename == '':
            return jsonify({"error": "O arquivo está vazio"}), 400

        # Verificar a extensão do arquivo
        extensoes_permitidas = ['xlsx', 'csv', 'xls']  # Exemplo de lista de extensões permitidas
        extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao_arquivo not in extensoes_permitidas:
            extensoes_permitidas_str = ', '.join(extensoes_permitidas)
            return jsonify({"error": f"Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}"}), 400

        # Leitura do arquivo
        if extensao_arquivo in ['xlsx', 'xls', 'csv']:
            try:
                rmanifest = pd.read_excel(arquivo)
            except Exception as e:
                return jsonify({"error": f"Erro na leitura do arquivo {e}"}), 400

            # Remover protocolos duplicados
            rmanifest.drop_duplicates(subset=['PROTOCOLO'], inplace=True)

            # Obter o órgão especificado pelo usuário, se fornecido
            orgao_desejado = request.form.get('orgao')
            if orgao_desejado:
                orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                manifestacoes_orgao = rmanifest[rmanifest['ÓRGÃO'].str.upper() == orgao_desejado]

                # Calcular o total de manifestações por tipo para o órgão especificado
                total_manifestacoes_tipo = manifestacoes_orgao['TIPO DE MANIFESTAÇÃO'].value_counts().to_dict()

                return jsonify(total_manifestacoes_tipo), 200
            else:
                # Se o órgão não foi especificado, calcular o total de manifestações por tipo para todos os órgãos
                total_manifestacoes_tipo = rmanifest['TIPO DE MANIFESTAÇÃO'].value_counts().to_dict()

                return jsonify(total_manifestacoes_tipo), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ouvidoria/total-respondidas', methods=['POST'])
@jwt_required()
def respondidas():
    try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        # Obter o arquivo enviado
        arquivo = request.files['file']

        # Verificar se o arquivo está vazio
        if arquivo.filename == '':
            return jsonify({"error": "O arquivo está vazio"}), 400

        # Verificar a extensão do arquivo
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao_arquivo not in extensoes_permitidas:
            extensoes_permitidas_str = ', '.join(extensoes_permitidas)
            return jsonify({"error": f"Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}"}), 400

        # Leitura do arquivo
        if extensao_arquivo in ['xlsx', 'xls', 'csv']:
            try:
                rmanifest = pd.read_excel(arquivo)
            except pd.errors.ParserError as e:
                return jsonify({"error": f"Erro na leitura do arquivo: {str(e)}"}), 400
            
            colunas_arquivo = rmanifest.columns.tolist()
            colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'DATA DE RESPOSTA']
            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return jsonify({"error": "Arquivo errado, por favor importar o relatório de manifestações"}), 400
            
            try:
                # Remover protocolos duplicados
                rmanifest.drop_duplicates(subset=['PROTOCOLO'], inplace=True)
                
                # Filtrar as respostas do ano atual
                ano_atual = pd.Timestamp.now().year
                manifest_respondidas = rmanifest.dropna(subset=['DATA DE RESPOSTA'])
                manifest_respondidas['DATA DE RESPOSTA'] = pd.to_datetime(manifest_respondidas['DATA DE RESPOSTA'], dayfirst=True)
                manifest_respondidas = manifest_respondidas[manifest_respondidas['DATA DE RESPOSTA'].dt.year == ano_atual]
                manifest_por_orgao = manifest_respondidas.groupby('ÓRGÃO').size()

                # Obter o órgão especificado pelo usuário, se fornecido
                orgao_desejado = request.form.get('orgao')
                if orgao_desejado:
                    orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                    # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                    manifestacoes_orgao = manifest_por_orgao[manifest_por_orgao.index.str.upper() == orgao_desejado]

                    return jsonify(manifestacoes_orgao.to_dict()), 200
                else:
                    # Se o órgão não foi especificado, calcular o total de manifestações por tipo para todos os órgãos
                    return jsonify(manifest_por_orgao.to_dict()), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ouvidoria/tempo-medio', methods=['POST'])
@jwt_required()
def tempo_medio():
    try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        # Obter o arquivo enviado
        arquivo = request.files['file']

        # Verificar se o arquivo está vazio
        if arquivo.filename == '':
            return jsonify({"error": "O arquivo está vazio"}), 400

        # Verificar a extensão do arquivo
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao_arquivo not in extensoes_permitidas:
            extensoes_permitidas_str = ', '.join(extensoes_permitidas)
            return jsonify({"error": f"Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}"}), 400

        # Leitura do arquivo
        if extensao_arquivo in ['xlsx', 'xls', 'csv']:
            try:
                rmanifest = pd.read_excel(arquivo)
            except Exception as e:
                return jsonify({"error": f"Erro na leitura do arquivo: {str(e)}"}), 400
            
            colunas_arquivo = rmanifest.columns.tolist()
            colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'DATA DE RESPOSTA', 'PERÍODO DE ATENDIMENTO EM DIAS']
            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return jsonify({"error": "Arquivo errado, por favor importar o relatório de manifestações"}), 400
            
            try:
                # Remover protocolos duplicados
                rmanifest.drop_duplicates(subset=['PROTOCOLO'], inplace=True)
                
                # Filtrar as respostas do ano atual
                ano_atual = pd.Timestamp.now().year
                manifest_com_tempo = rmanifest.dropna(subset=['PERÍODO DE ATENDIMENTO EM DIAS'])
                manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'] = pd.to_numeric(manifest_com_tempo['PERÍODO DE ATENDIMENTO EM DIAS'])
                tempo_medio_por_orgao = round(manifest_com_tempo.loc[(rmanifest["DATA DE RESPOSTA"] != 0) & (rmanifest["DATA DE RESPOSTA"] != ano_atual) ].groupby('ÓRGÃO')['PERÍODO DE ATENDIMENTO EM DIAS'].mean(), 2)
    
                # Obter o órgão especificado pelo usuário, se fornecido
                orgao_desejado = request.form.get('orgao')
                if orgao_desejado:
                    orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                    # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                    manifestacoes_orgao = tempo_medio_por_orgao[tempo_medio_por_orgao.index.str.upper() == orgao_desejado]

                    return jsonify(manifestacoes_orgao.to_dict()), 200
                else:
                    # Se o órgão não foi especificado, calcular o total de manifestações por tipo para todos os órgãos
                    return jsonify(tempo_medio_por_orgao.to_dict()), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/ouvidoria/ranking-assunto', methods=['POST'])
@jwt_required()
def ranking():
    try:
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400

        # Obter o arquivo enviado
        arquivo = request.files['file']

        # Verificar se o arquivo está vazio
        if arquivo.filename == '':
            return jsonify({"error": "O arquivo está vazio"}), 400

        # Verificar a extensão do arquivo
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()
        if extensao_arquivo not in extensoes_permitidas:
            extensoes_permitidas_str = ', '.join(extensoes_permitidas)
            return jsonify({"error": f"Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}"}), 400

        # Leitura do arquivo e contagem dos assuntos
        if extensao_arquivo in ['xlsx', 'xls', 'csv']:
            try:
                rmanifest = pd.read_excel(arquivo)
            except Exception as e:
                return jsonify({"error": f"Erro na leitura do arquivo: {str(e)}"}), 400

            colunas_arquivo = rmanifest.columns.tolist()
            colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'DATA DE RESPOSTA', 'ASSUNTO']
            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return jsonify({"error": "Arquivo errado, por favor importar o relatório de manifestações"}), 400

            try:
                # Remover protocolos duplicados
                rmanifest.drop_duplicates(subset=['PROTOCOLO'], inplace=True)

                # Obter o órgão especificado pelo usuário, se fornecido
                orgao_desejado = request.form.get('orgao')
                if orgao_desejado:
                    orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas
                    ranking = rmanifest['ASSUNTO'].value_counts().reset_index()
                    ranking = ranking.rename(columns={'index': 'Assunto', 'ASSUNTO': 'Quantidade'})
                    ranking_uo = ranking.loc[ranking['ÓRGÃO'] == orgao_desejado]
                    ranking_uo = ranking_uo.drop(columns=['ÓRGÃO'])

                    # Ordenar o ranking por quantidade em ordem decrescente
                    ranking_uo = ranking_uo.sort_values(by='Quantidade', ascending=False)

                    # Converter o DataFrame em uma lista de dicionários
                    result = ranking_uo.to_dict(orient='records')

                    return jsonify(result), 200
                else:
                    # Se o órgão não foi especificado, calcular o total de manifestações por tipo para todos os órgãos
                    ranking = rmanifest['ASSUNTO'].value_counts().reset_index()
                    ranking = ranking.rename(columns={'index': 'Assunto', 'ASSUNTO': 'Demanda'})

                    # Ordenar o ranking por quantidade em ordem decrescente
                    ranking = ranking.sort_values(by='Demanda', ascending=False)

                    # Converter o DataFrame em uma lista de dicionários
                    result = ranking.to_dict(orient='records')

                    return jsonify(result), 200
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500