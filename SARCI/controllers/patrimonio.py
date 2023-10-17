import pandas as pd 
import tabula
import pdfplumber
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.options.display.float_format = '{:.2f}'.format


def dir(arq):
    "Armazena o diretório do arquivo"
    d = arq[0].rfind('/'or '\\')
    return (arq[:d+1])


def almoxerifado(palmo): #palmo = planilha referente ao almoxerifado
    import getpass
    #usuario = getpass.getuser()

    # ler tabela(s)
    todos_pdfs = [] #cria uma lista vazia onde será armazenados os caminhos relativos
    for files in palmo:
        pagina_pdf = tabula.read_pdf(files, pages='all', guess=False) #lê cada caminho relativo e transforma o pdf num dataframe
        todos_pdfs.extend(pagina_pdf)

    # Converter a lista dfs em um DataFrame pandas
    df = pd.concat(todos_pdfs) #pegando todos os pdfs e transformando em um só dataframe!

    # Procurar a substring "TOTAL GERAL" em todas as colunas
    ocorrencias = df.apply(lambda x: x.astype(str).str.contains("TOTAL GERAL:", na=False))
    # Selecionar apenas as linhas com ocorrências
    df_repeticoes = df.loc[ocorrencias.any(axis=1)]
    #tira as colunas que só possuem NaN
    df_repeticoes = df_repeticoes.dropna(axis='columns', how='all')
    
    #armazena na variavel valor as ocorrências de strings que começam com R$ através do método .str.startwith
    valor = df_repeticoes[df_repeticoes.apply(lambda x: x.astype(str).str.startswith("R$ "), axis=1)].stack().tolist()
    #armazena na variavel quantidade as ocorrências das strings que são opostas a função x, isto é, aquelas que não começam com R$
    quantidade = df_repeticoes[df_repeticoes.apply(lambda x: ~(x.astype(str).str.startswith("R$ ") | x.astype(str).str.startswith("T")), axis=1)].stack().tolist()

    #remove caracteres indesejados e transforma o restante em ponto flutuante
    valor = [float(v.replace("R$", "").replace(".", "").replace(",", ".")) for v in valor]
    quantidade = [float(q.replace(".","").replace(",",".")) for q in quantidade]

    #soma todos os valores na lista
    total_valores = sum(valor)
    total_quantidade = sum(quantidade)

    #cria um dataFrame com as informações dispostas
    info = {'QUANTIDADE': [total_quantidade], 'Valor': [total_valores]}
    df_almoxerifado = pd.DataFrame(info, index=['TOTAL GERAL'])
    df_almoxerifado.to_excel('Almoxerifado-CGM.xlsx')
    #df_almoxerifado.to_excel(f'C:/Users/{usuario}/Downloads/Almoxerifado-CGM.xlsx')
    return df_almoxerifado


def bensmoveis(ri):
    # Abrir o arquivo PDF
    with pdfplumber.open(ri) as pdf:
        tables = []  # Lista para armazenar as tabelas extraídas

        # Iterar sobre as páginas do PDF
        for page in pdf.pages:
            # Extrair as tabelas da página
            extracted_tables = page.extract_tables()
            
            # Adicionar as tabelas extraídas à lista
            tables.extend(extracted_tables)

    df = pd.DataFrame(tables)
    dados_uteis = df.apply(lambda x: x.astype(str).str.contains("VALOR TOTAL UNIDADE GESTORA:", na=False))
    df_util = df.loc[dados_uteis.any(axis=1)]

    #FILTRA AS INFORMAÇÕES DE TODOS AS PÁGINAS, PEGANDO SOMENTE AS QUE SÃO NECESSÁRIAS PARA GENTE
    qtd_total = df_util[df_util.apply(lambda x: x.astype(str).str.contains("QUANTIDADE TOTAL UNIDADE GESTORA"), axis = 0)].stack().tolist()
    vlr_total = df_util[df_util.apply(lambda x: x.astype(str).str.contains("VALOR TOTAL UNIDADE GESTORA"), axis = 0)].stack().tolist()
    qtd_bens_leilao = df_util[df_util.apply(lambda x: x.astype(str).str.contains("QUANTIDADE DE BENS RECOLHIDO PARA LEILÃO"), axis = 0)].stack().tolist()
    qtd_bens_terceiros = df_util[df_util.apply(lambda x: x.astype(str).str.contains("QUANTIDADE TOTAL DE BENS DE TERCEIROS"), axis = 0)].stack().tolist()
    qtd_bens_inserviveis = df_util[df_util.apply(lambda x: x.astype(str).str.contains("QUANTIDADE DE BENS NO DEPOSITO DE INSERVÍVEL"), axis = 0)].stack().tolist()
    
    #GERAR UM DICIONARIO COM AS INFORMAÇÕES
    data = {
        'QUANTIDADE TOTAL UNIDADE GESTORA': qtd_total[0][-1],
        'VALOR TOTAL UNIDADE GESTORA' : vlr_total[0][-1],
        'QUANTIDADE DE BENS RECOLHIDOS PARA LEILÃO' : qtd_bens_leilao[0][-1],
        'QUANTIDADE TOTAL DE BENS DE TERCEIROS' : qtd_bens_terceiros[0][1],
        'QUANTIDADE DE BENS NO DEPOSITO DE INSERVIVEL' : qtd_bens_inserviveis[0][-1]
    }

    #gera o dataframe e passa para excel
    df_inventario = pd.DataFrame(data, index=[''])
    df_inventario.to_excel('Inventario-CGM.xlsx')
    #df_inventario.to_excel(f'{dir(ri)}Inventário.xlsx',index=False)
    return df_inventario


