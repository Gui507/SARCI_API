from SARCI.config import app
from flask import request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required
import pandas as pd
from datetime import timedelta
import psycopg2
import dotenv
import os

dotenv.load_dotenv()
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
            access_token = create_access_token(identity=resultado[0], expires_delta=timedelta(minutes=2))
            return jsonify({'access_token': access_token})
        else:
            return jsonify({'message': 'Invalid credentials'})


'''# TESTE EM CASA (SEM BANCO DE DADOS)
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
        access_token = create_access_token(identity=matching_user['id'], expires_delta=timedelta(minutes=20))
        return jsonify({'access_token': access_token})
    else:
        return jsonify({'message': 'Invalid credentials'})
    '''

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
    if extensao_arquivo == 'xlsx' or 'xls': 
        P1 = pd.read_excel(arquivo, header=3)
    elif extensao_arquivo == 'csv':
        P1 = pd.read_csv(arquivo, header=3)

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
        
