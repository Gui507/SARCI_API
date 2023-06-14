'''Application Programming Interface (API) é uma ferramenta de conexão entre software, de maneira prática, é como o garçom de um restaurante, onde você faz um pedido (requisição), ele manda para a cozinha (serviço/programa conectado) e traz o seu prato pronto (resposta).
Objetivo - Criar uma API que acesse o sistema SARCI, colete e mande os arquivos, informaçoes e anexos necessários para a geração do RCIG e retorne um arquivo preenchido e editavel
URL base - local para onde será feita as requisiçoes. SARCI
Endpoints - tipos de funcionalidades caminho/ rota a ser seguida para fazer uma requisição
Recurso - Dea, contrato'''
from flask import Flask, jsonify, request, render_template
import tkinter.filedialog
import pandas as pd
app = Flask(__name__)
@app.route('/', methods = ['GET', 'POST'])

def dea():
    if request.method == 'GET':
        print('Importe o Relátorio de Empenho e Destaques Analíticos')
        re = tkinter.filedialog.askopenfilename()
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
        # despezas_de_execicios_anteriores.to_excel(f'{dir(re)}DEA.xlsx', index=True)
        return despezas_de_execicios_anteriores.to_json(orient='columns')
    else:
        return jsonify({'message': 'Método POST não suportado'})

    
if __name__ == '__main__':
    app.run()

