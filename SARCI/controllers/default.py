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
    if 'file' not in request.files:
        return 'Nenhum arquivo enviado', 400
    re = request.files['file']
    P1 = pd.read_excel(re, header = 3)
    # Filtra linhas onde o valor de 'Despes' termina em '92'
    mask = P1['Despes'].astype(str).str.endswith('92')

    # Soma os valores correspondentes
    soma_dea = P1.loc[mask, 'Vlr. Emp. Líquido'].sum()
    soma_sem_dea = P1.loc[~mask, 'Vlr. Emp. Líquido'].sum()

    valor_total = soma_dea + soma_sem_dea
    execucao_dea = round((soma_dea / valor_total) * 100, 2)
    despezas_de_execicios_anteriores = pd.DataFrame([soma_dea,valor_total,execucao_dea],index=['Valor empenhado com DEA', 'Valor total empenhado', 'Índice de Execução de DEA'])
    # print(despezas_de_execicios_anteriores)
    return despezas_de_execicios_anteriores.to_json(orient='columns')

