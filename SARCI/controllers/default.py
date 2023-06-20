from SARCI import app
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import timedelta
import psycopg2

def conectar_bd():
    return psycopg2.connect(host="172.30.100.142", database="sarci", port=5432, user="postgres", password="Sarci23")

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
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
        access_token = create_access_token(identity=resultado[0], expires_delta=timedelta(minutes=2))
        return jsonify({'access_token': access_token})
    else:
        return jsonify({'message': 'Invalid credentials'})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Acess granted to protected resource'})


        

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

    # Verificar se as colunas existem no arquivo
    colunas_obrigatorias = ['Despes', 'Vlr. Emp. Líquido']
    try:
        if extensao_arquivo == '.xlsx':
            P1 = pd.read_excel(arquivo, header=3)
        elif extensao_arquivo == '.csv':
            P1 = pd.read_csv(arquivo, header=3)
        elif extensao_arquivo == '.txt':
            P1 = pd.read_csv(arquivo, sep='\t', header=3)

        colunas_arquivo = P1.columns.tolist()

        for coluna in colunas_obrigatorias:
            if coluna not in colunas_arquivo:
                return f'A coluna "{coluna}" não foi encontrada no arquivo', 400
    except Exception as e:
        return f'Ocorreu um erro ao processar o arquivo: {str(e)}', 500

    # Restante do seu código para processar o arquivo
    mask = P1['Despes'].astype(str).str.endswith('92')
    soma_dea = P1.loc[mask, 'Vlr. Emp. Líquido'].sum()
    soma_sem_dea = P1.loc[~mask, 'Vlr. Emp. Líquido'].sum()
    valor_total = soma_dea + soma_sem_dea
    execucao_dea = round((soma_dea / valor_total) * 100, 2)
    despezas_de_execicios_anteriores = pd.DataFrame([soma_dea,valor_total,execucao_dea],index=['Valor empenhado com DEA', 'Valor total empenhado', 'Índice de Execução de DEA'])
    return despezas_de_execicios_anteriores.to_json(orient='columns')
  

