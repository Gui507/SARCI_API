from SARCI import app
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import timedelta
import psycopg2

def conectar_bd():
    return psycopg2.connect(host="172.30.100.142", database="sarci", port=5432, user="postgres", password="Sarci23")

def criar_tabela():
    # Conecta ao banco de dados
    conexao = conectar_bd()
    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()
    # Define o comando SQL para criar a tabela usuarios
    sql = """CREATE TABLE usuarios (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) NOT NULL,,
        senha VARCHAR(50) NOT NULL
    )"""
    # Executa o comando SQL
    cursor.execute(sql)
    # Salva as alterações no banco de dados
    conexao.commit()
    # Fecha o cursor e a conexão
    cursor.close()
    conexao.close()

# Define uma rota para acessar a função criar_tabela
@app.route("/criar_tabela", methods=['POST'])
def index():
    # Chama a função criar_tabela
    criar_tabela()
    # Retorna uma mensagem de sucesso
    return "Tabela usuarios criada com sucesso!"
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
       'password': 'blablabla123'
    }
    ]

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    matching_user = next((user for user in db if user['username'] == username and user['password'] == password))

    if matching_user:
        access_token = create_access_token(identity=matching_user['id'], expires_delta=timedelta(minutes=2))
        return jsonify({'access_token': access_token})

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

