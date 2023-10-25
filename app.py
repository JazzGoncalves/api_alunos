from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import sqlite3
import os
from werkzeug.utils import url_quote


app = Flask(__name__)
api = Api(app)

def init_db():
    with app.app_context():
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER,
                nota_primeiro_semestre REAL,
                nota_segundo_semestre REAL,
                nome_professor TEXT,
                numero_sala INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()

init_db()

class AlunoResource(Resource):
    def get(self, aluno_id):
        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,))
        aluno = cursor.fetchone()
        conn.close()
        if aluno:
            aluno_data = {
                'id': aluno[0],
                'nome': aluno[1],
                'idade': aluno[2],
                'nota_primeiro_semestre': aluno[3],
                'nota_segundo_semestre': aluno[4],
                'nome_professor': aluno[5],
                'numero_sala': aluno[6]
            }
            return aluno_data
        else:
            return {'message': 'Aluno não encontrado'}, 404

    def put(self, aluno_id):
        parser = reqparse.RequestParser()
        parser.add_argument('nome')
        parser.add_argument('idade', type=int)
        parser.add_argument('nota_primeiro_semestre', type=float)
        parser.add_argument('nota_segundo_semestre', type=float)
        parser.add_argument('nome_professor')
        parser.add_argument('numero_sala', type=int)
        
        args = parser.parse_args()
        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE alunos SET nome=?, idade=?, nota_primeiro_semestre=?, '
                       'nota_segundo_semestre=?, nome_professor=?, numero_sala=? WHERE id=?',
                       (args['nome'], args['idade'], args['nota_primeiro_semestre'],
                        args['nota_segundo_semestre'], args['nome_professor'], args['numero_sala'], aluno_id))
        conn.commit()
        conn.close()
        return {'message': 'Aluno atualizado com sucesso'}

    def delete(self, aluno_id):
        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
        conn.commit()
        conn.close()
        return {'message': 'Aluno excluído com sucesso'}

class AlunosResource(Resource):
    def get(self):
        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alunos')
        alunos = cursor.fetchall()
        conn.close()
        alunos_data = []
        for aluno in alunos:
            aluno_data = {
                'id': aluno[0],
                'nome': aluno[1],
                'idade': aluno[2],
                'nota_primeiro_semestre': aluno[3],
                'nota_segundo_semestre': aluno[4],
                'nome_professor': aluno[5],
                'numero_sala': aluno[6]
            }
            alunos_data.append(aluno_data)
        return alunos_data

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('nome')
        parser.add_argument('idade', type=int)
        parser.add_argument('nota_primeiro_semestre', type=float)
        parser.add_argument('nota_segundo_semestre', type=float)
        parser.add_argument('nome_professor')
        parser.add_argument('numero_sala', type=int)

        args = parser.parse_args()
        conn = sqlite3.connect('escola.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO alunos (nome, idade, nota_primeiro_semestre, '
                       'nota_segundo_semestre, nome_professor, numero_sala) '
                       'VALUES (?, ?, ?, ?, ?, ?)',
                       (args['nome'], args['idade'], args['nota_primeiro_semestre'],
                        args['nota_segundo_semestre'], args['nome_professor'], args['numero_sala']))
        conn.commit()
        conn.close()
        return {'message': 'Aluno adicionado com sucesso'}, 201

api.add_resource(AlunosResource, '/alunos')
api.add_resource(AlunoResource, '/alunos/<int:aluno_id>')

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

if __name__ == '__main__':
    debug_mode = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)