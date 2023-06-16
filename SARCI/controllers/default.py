from SARCI import app
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import timedelta
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

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    matching_user = next((user for user in db if user['username'] == username and user['password'] == password))

    if matching_user:
        access_token = create_access_token(identity=matching_user['id'], expires_delta=timedelta(seconds=30))
        return jsonify({'access_token': access_token})

    return jsonify({'message': 'Invalid credentials'})

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    return jsonify({'message': 'Acess granted to protected resource'})




@app.route('/', methods = ['POST'])
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
    print(despezas_de_execicios_anteriores)
    return despezas_de_execicios_anteriores.to_json(orient='columns')

