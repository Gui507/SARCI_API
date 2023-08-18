'''Application Programming Interface (API) é uma ferramenta de conexão entre software, de maneira prática, é como o garçom de um restaurante, onde você faz um pedido (requisição), ele manda para a cozinha (serviço/programa conectado) e traz o seu prato pronto (resposta).
Objetivo - Criar uma API que acesse o sistema SARCI, colete e mande os arquivos, informaçoes e anexos necessários para a geração do RCIG e retorne um arquivo preenchido e editavel
URL base - local para onde será feita as requisiçoes. SARCI
Endpoints - tipos de funcionalidades caminho/ rota a ser seguida para fazer uma requisição
Recurso - Dea, contrato'''
from flask import Flask
from flask_jwt_extended import JWTManager
# from flask_sqlalchemy import SQLAlchemy
# import dotenv
# import os
#dotenv.load_dotenv()
#app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
#db = SQLAlchemy(app)
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'my_secret_key'
jwt = JWTManager(app)


from Sarci.controllers import default

