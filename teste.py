import tkinter.filedialog
import pandas as pd
def dea():
    file = tkinter.filedialog.askopenfilename()
    # Verificar se o arquivo foi enviado
    if 'file' not in file:
        return 'Nenhum arquivo enviado', 400

    # Obter o arquivo enviado
    arquivo = file['file']

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
        