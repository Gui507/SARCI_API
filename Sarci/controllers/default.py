from Sarci.config import app
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
import pandas as pd
from datetime import timedelta
from Sarci.controllers import contratos, ouvidoria, transparencia
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

def verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo,header=0):
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
    
    if extensao_arquivo in ['pdf', 'docx']:
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


#@app.route('/ouvidoria/total-de-manifestacoes', methods=['POST'])
#@jwt_required()
#def total_manifest():
#    try:
#        extensoes_permitidas = ['xlsx', 'csv', 'xls']
#        colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
#        nome_do_arquivo='Relatório de Manifestação'
#        orgao_desejado = request.form.get('orgao')
#        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
#        if not arquivo_valido:
#            return arquivo, 400
#
#        a = ouvidoria.total(arquivo,orgao_desejado)  # Chame a função dea do seu arquivo contratos.py
#        # Converta o resultado em JSON
#
#        return a  # Retorne o JSON como resposta
#
#    except Exception as e:
#        return jsonify({"error": str(e)}), 500


@app.route('/ouvidoria/total-tipos', methods=['POST'])
@jwt_required()
def contagem():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
        nome_do_arquivo='Relatório de Manifestação'
        orgao_desejado = request.form.get('orgao')
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
        if not arquivo_valido:
            return arquivo, 400

        a = ouvidoria.contagem(arquivo, orgao_desejado)  # Chame a função dea do seu arquivo contratos.py
            # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ouvidoria/total-respondidas', methods=['POST'])
@jwt_required()
def respondidas():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
        nome_do_arquivo='Relatório de Manifestação'
        orgao_desejado = request.form.get('orgao')
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
        if not arquivo_valido:
            return arquivo, 400

        a = ouvidoria.respondidas(arquivo, orgao_desejado)  # Chame a função dea do seu arquivo contratos.py
            # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ouvidoria/tempo-medio', methods=['POST'])
@jwt_required()
def tempo_medio():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
        nome_do_arquivo='Relatório de Manifestação'
        orgao_desejado = request.form.get('orgao')
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
        if not arquivo_valido:
            return arquivo, 400

        a = ouvidoria.tempomedioresp(arquivo, orgao_desejado)  # Chame a função dea do seu arquivo contratos.py
            # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ouvidoria/ranking-assunto', methods=['POST'])
@jwt_required()
def ranking():
    try:
        extensoes_permitidas = ['xlsx', 'csv', 'xls']
        colunas_obrigatorias = ['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
        nome_do_arquivo='Relatório de Manifestação'
        orgao_desejado = request.form.get('orgao')
        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
        if not arquivo_valido:
            return arquivo, 400

        a = ouvidoria.ranking_assunto(arquivo, orgao_desejado)  # Chame a função dea do seu arquivo contratos.py
            # Converta o resultado em JSON

        return a  # Retorne o JSON como resposta

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ouvidoria/total-de-manifestacoes', methods=['POST'])
@jwt_required()
def total_manifest():
    try:
        extensoes_permitidas=['xlsx','csv', 'xls']
        colunas_obrigatorias=['PROTOCOLO', 'ÓRGÃO', 'TIPO DE MANIFESTAÇÃO']
        nome_do_arquivo = 'Relatório de Manifestação'

        arquivo_valido, arquivo = verificar_arquivo(request, extensoes_permitidas, colunas_obrigatorias, nome_do_arquivo, header=0)
        if not arquivo_valido:
            return arquivo, 400
        
        orgao_desejado = request.form.get('orgao')
        resultado = ouvidoria.total(arquivo, orgao_desejado)
        return jsonify(resultado)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
