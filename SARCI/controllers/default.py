from SARCI import app
from flask import request, jsonify, render_template,create_access_token
from werkzeug.utils import secure_filename
import tkinter.filedialog
import pandas as pd


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if username != db.username or  password != db.password:
        return jsonify({'msg': "Senha ou usuario invalidos"}), 401
    
    token_de_acesso = create_access_token(identify=username)
    return jsonify(access_token=token_de_acesso), 200


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

