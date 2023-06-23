from flask import Flask, jsonify, url_for, redirect, request
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
api = Api(app)



class CriaUser(Resource):
    def get(self):
        return jsonify({
            'status': 'SHOW!!','message': 'DEU TUDO CERTO PORRA'
        })

api.add_resource(CriaUser, '/CriaUser', methods=['GET'])

if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)


