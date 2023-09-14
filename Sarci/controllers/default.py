from Sarci.config import app
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
import pandas as pd
from datetime import timedelta
from Sarci.controllers import contratos
import json
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

def verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo,header):
    # Verificar se o arquivo foi enviado
    if 'file' not in request.files:
        return False, 'Nenhum arquivo enviado'

    arquivo = request.files['file']

    # Verificar se o arquivo está vazio
    if arquivo.filename == '':
        return False, 'O arquivo está vazio'

    extensao_arquivo = arquivo.filename.rsplit('.', 1)[1].lower()

    # Verificar a extensão do arquivo
    if extensao_arquivo not in extensoes_permitidas:
        extensoes_permitidas_str = ', '.join(extensoes_permitidas)
        return False, f'Formato de arquivo inválido. Por favor, envie um arquivo com as extensões permitidas: {extensoes_permitidas_str}'

    if extensao_arquivo in ['xlsx', 'xls', 'csv']:
        try:
            P1 = pd.read_excel(arquivo, header=header)
        except Exception as e:
            return False, f"Erro na leitura do arquivo {e}"

        colunas_arquivo = P1.columns.tolist()
        for coluna in colunas_obrigatorias:
            if coluna not in colunas_arquivo:
                return False, f'Arquivo errado errado, por favor importe o {nome_do_arquivo} '

    return True, arquivo


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


@app.route('/dea', methods=['POST'])
@jwt_required()
def dea():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['Despes', 'Vlr. Emp. Líquido']
        nome_do_arquivo='Relatório de Destaques e Empenhos Analítico'
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=3)
        if not arquivo_valido:
            return arquivo, 400

        a = contratos.dea(arquivo)  # Chame a função dea do seu arquivo contratos.py
          # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500
   

@app.route('/despezas', methods = ['POST'])
@jwt_required()
def despezas_route():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['Descrição do Programa', 'Sd Dot.Atual', 'Emp. No Mês', 'Liq. No Mês']
        nome_do_arquivo='Relatório Acompanhamento e Execução Orçamentaria'
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=1)
        if not arquivo_valido:
            return arquivo, 400

        a = contratos.despezas(arquivo)  # Chame a função dea do seu arquivo contratos.py
          # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    

@app.route('/transparencia/ranking-assunto', methods=['POST'])
@jwt_required()
def ranking_assunto():
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
                rpedidos = pd.read_excel(arquivo, header=4)
            except Exception as e:
                return f"Erro na leitura do arquivo {e}", 400

            colunas_arquivo = rpedidos.columns.tolist()
            colunas_obrigatorias = ['Orgão (SIC)','Situação\n(*)','Assunto','Nº de pedidos fora do prazo (> 20 dias)','Quantidade','Recurso de 1ª Instância','Recurso de 2ª Instância','Recurso de 3ª Instância',]

            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return f'Arquivo errado, por favor importar o relatório de pedidos', 400

            # Obter o órgão especificado pelo usuário, se fornecido
            orgao_desejado = request.form.get('orgao')

            if orgao_desejado:
                orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                manifestacoes_orgao = rpedidos[rpedidos['ÓRGÃOS'].str.upper() == orgao_desejado]

                # Calcular o total de manifestações para o órgão especificado
                total_manifestacoes = len(manifestacoes_orgao)

                return f'Total de pedidos para o órgão {orgao_desejado}: {total_manifestacoes}', 200
            else:
                # Se o órgão não foi especificado, calcular o total de manifestações para todos os órgãos
                total_manifestacoes = rpedidos.groupby(['ÓRGÃOS']).size()

                return f'Total de pedidos de todos os órgãos: {total_manifestacoes}', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Incluir o código da função pedidos aqui
    df_base = pd.read_excel(arquivo, header=4)
    df_final = df_base[['Nº de Pedidos', 'Nº de pedidos dentro do prazo (20 dias)', 'Nº de pedidos fora do prazo (> 20 dias)', 'Tempo Médio de Resposta do Pedido', 'Recurso de 1ª Instância', 'Recurso de 2ª Instância', 'Recurso de 3ª Instância']]
    #df_final.to_excel(f'{dir(arquivo)}Resultados Transparencia - {orgao_desejado}.xlsx',index=False)
    #df_final.to_excel('Resultados Transparencia-CGM.xlsx')
    return df_final


@app.route('/transparencia/pedidos', methods=['POST'])
@jwt_required()
def pedidos():
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
                rpedidos = pd.read_excel(arquivo, header=4)
            except Exception as e:
                return f"Erro na leitura do arquivo {e}", 400

            colunas_arquivo = rpedidos.columns.tolist()
            colunas_obrigatorias = ['ÓRGÃOS','Nº de Pedidos','Nº de pedidos dentro do prazo (20 dias)','Nº de pedidos fora do prazo (> 20 dias)','Tempo Médio de Resposta do Pedido ','Recurso de 1ª Instância','Recurso de 2ª Instância','Recurso de 3ª Instância',]

            for coluna in colunas_obrigatorias:
                if coluna not in colunas_arquivo:
                    return f'Arquivo errado, por favor importar o relatório de pedidos', 400

            # Obter o órgão especificado pelo usuário, se fornecido
            orgao_desejado = request.form.get('orgao')

            if orgao_desejado:
                orgao_desejado = orgao_desejado.upper()  # Converter para maiúsculas

                # Filtrar as manifestações pelo órgão especificado (insensível a maiúsculas/minúsculas)
                manifestacoes_orgao = rpedidos[rpedidos['ÓRGÃOS'].str.upper() == orgao_desejado]

                # Calcular o total de manifestações para o órgão especificado
                total_manifestacoes = len(manifestacoes_orgao)

                return f'Total de pedidos para o órgão {orgao_desejado}: {total_manifestacoes}', 200
            else:
                # Se o órgão não foi especificado, calcular o total de manifestações para todos os órgãos
                total_manifestacoes = rpedidos.groupby(['ÓRGÃOS']).size()

                return f'Total de pedidos de todos os órgãos: {total_manifestacoes}', 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Incluir o código da função pedidos aqui
    df_base = pd.read_excel(arquivo, header=4)
    df_final = df_base[['Nº de Pedidos', 'Nº de pedidos dentro do prazo (20 dias)', 'Nº de pedidos fora do prazo (> 20 dias)', 'Tempo Médio de Resposta do Pedido', 'Recurso de 1ª Instância', 'Recurso de 2ª Instância', 'Recurso de 3ª Instância']]
    #df_final.to_excel(f'{dir(arquivo)}Resultados Transparencia - {orgao_desejado}.xlsx',index=False)
    #df_final.to_excel('Resultados Transparencia-CGM.xlsx')
    return df_final