from flask import Flask, jsonify, request
from flask_cors import CORS
from argon2 import PasswordHasher
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import os
import ssl
import sqlite3
import datetime
import json

app = Flask(__name__)

# Configuração JWT
app.config['JWT_SECRET_KEY'] = 'teste'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=10)
jwt = JWTManager(app)

# Configuração CORS
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    allowed = [
        'https://localhost:5000', 'http://localhost:5000',
        'https://127.0.0.1:5000', 'http://127.0.0.1:5000',
        'https://localhost:3000', 'http://localhost:3000',
        'https://127.0.0.1:3000', 'http://127.0.0.1:3000'
    ]
    if origin in allowed:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Origin,Accept'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# Passwords
USERS = {
    "admin@mail.com": "$argon2id$v=19$m=65536,t=3,p=4$laoLrteVYNU4Ltkv4R696Q$1qR+tdX4Pb7SJW5dJ3ntS0db+949+CV2kXK/oq1bkkk",
    "teste@mail.com": "$argon2id$v=19$m=65536,t=3,p=4$V6uXrWPph/ge7waxo3HXlg$BMf+GJD3z+mu8/5HwRlqS9fxy5ddAzSj7c3Ew03bWWg"
}

# Login
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    ph = PasswordHasher()
    if request.method == 'OPTIONS':
        return '', 200
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in USERS:
        hashed_password = USERS[username]
        try:
            if ph.verify(hashed_password, password):
                access_token = create_access_token(identity=username)
                return jsonify({
                    "message": "Login successful!",
                    "username": username,
                    "access_token": access_token
                }), 200
        except Exception:
            pass
    return jsonify({"message": "Invalid credentials"}), 401

# Rotas SQL
@app.route("/get-person-by-name/<name>", methods=['GET', 'OPTIONS'])
@jwt_required()
def get_person_by_name(name):
    if request.method == 'OPTIONS':
        return '', 200
    cpf_db_path = os.environ.get('CPF_DB_PATH', 'db/basecpf.db')
    try:
        conn_cpf = sqlite3.connect(cpf_db_path)
        cursor_cpf = conn_cpf.cursor()
        cursor_cpf.execute("SELECT * FROM cpf WHERE nome LIKE UPPER(?)", ('%' + name + '%',))
        results = cursor_cpf.fetchall()
        conn_cpf.close()
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    'cpf': row[0],
                    'nome': row[1],
                    'sexo': row[2],
                    'nasc': row[3]
                }
                cpf_list.append(cpf_info)
            return jsonify({'results': cpf_list}), 200
        else:
            return jsonify({'error': 'Nome não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-person-by-exact-name/<name>", methods=['GET', 'OPTIONS'])
@jwt_required()
def get_person_by_exact_name(name):
    if request.method == 'OPTIONS':
        return '', 200
    cpf_db_path = os.environ.get('CPF_DB_PATH', 'db/basecpf.db')
    try:
        conn_cpf = sqlite3.connect(cpf_db_path)
        cursor_cpf = conn_cpf.cursor()
        cursor_cpf.execute("SELECT * FROM cpf WHERE nome = UPPER(?)", (name,))
        results = cursor_cpf.fetchall()
        conn_cpf.close()
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    'cpf': row[0],
                    'nome': row[1],
                    'sexo': row[2],
                    'nasc': row[3]
                }
                cpf_list.append(cpf_info)
            return jsonify({'results': cpf_list}), 200
        else:
            return jsonify({'error': 'Nome não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-person-by-cpf/<cpf>", methods=['GET', 'OPTIONS'])
@jwt_required()
def get_person_by_cpf(cpf):
    if request.method == 'OPTIONS':
        return '', 200
    cpf_db_path = os.environ.get('CPF_DB_PATH', 'db/basecpf.db')
    try:
        conn_cpf = sqlite3.connect(cpf_db_path)
        cursor_cpf = conn_cpf.cursor()
        cursor_cpf.execute("SELECT * FROM cpf WHERE cpf = ?", (cpf,))
        results = cursor_cpf.fetchall()
        conn_cpf.close()
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    'cpf': row[0],
                    'nome': row[1],
                    'sexo': row[2],
                    'nasc': row[3]
                }
                cpf_list.append(cpf_info)
            return jsonify({'results': cpf_list}), 200
        else:
            return jsonify({'error': 'CPF não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@app.route("/get-person-cnpj-by-name-and-cpf/<name>/<cpf>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_name_and_cpf(name, cpf):
    if request.method == 'OPTIONS':
        return '', 200
    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        # First query: get CNPJs from socios
        cursor_cnpj.execute(
            "SELECT cnpj FROM socios WHERE (nome_socio LIKE UPPER(?) OR nome_representante LIKE UPPER(?)) AND cnpj_cpf_socio LIKE ?",
            ('%' + name + '%', '%' + name + '%', '%' + cpf[3:-2] + '%')
        )
        cnpj_rows = cursor_cnpj.fetchall()
        if not cnpj_rows:
            conn_cnpj.close()
            return jsonify({'error': 'Nome não encontrado'}), 404

        # Prepare list of CNPJs for the second query
        cnpj_list = [row[0] for row in cnpj_rows]
        results = []
        for cnpj in cnpj_list:
            cursor_cnpj.execute(
                "SELECT cnpj, nome_fantasia, uf FROM estabelecimento WHERE cnpj = ?",
                (cnpj,)
            )
            est = cursor_cnpj.fetchone()
            if est:
                results.append({
                    'cnpj': est[0],
                    'nome_fantasia': est[1],
                    'uf': est[2]
                })
        conn_cnpj.close()
        if results:
            return jsonify({'results': results}), 200
        else:
            return jsonify({'error': 'CNPJ não encontrado em estabelecimento'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-cnpj-person-by-cnpj/<cnpj>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_cnpj(cnpj):
    if request.method == 'OPTIONS':
        return '', 200
    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute(
            "SELECT cnpj, nome_fantasia, uf FROM estabelecimento WHERE cnpj = ?",
            (cnpj,)
        )
        results = cursor_cnpj.fetchall()
        cnpj_list = []
        for row in results:
            cnpj = row[0]
            cursor_cnpj.execute(
                "SELECT nome_socio, nome_representante, cnpj_cpf_socio FROM socios WHERE cnpj = ?",
                (cnpj,)
            )
            print(cnpj)
            socios = cursor_cnpj.fetchall()
            socios_list = [
                {
                    'nome_socio': s[0],
                    'nome_representante': s[1],
                    'cnpj_cpf_socio': s[2]
                } for s in socios
            ]
            cnpj_info = {
                'cnpj': row[0],
                'nome fantasia': row[1],
                'uf': row[2],
                'socios': socios_list
            }
            cnpj_list.append(cnpj_info)
        conn_cnpj.close()
        if cnpj_list:
            return jsonify({'results': cnpj_list}), 200
        else:
            return jsonify({'error': 'Não é sócio de nenhuma empresa'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

def create_ssl_context():
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('server.crt', 'server.key')
        print("Certificados encontrados, usando SSL")
        return context
    except FileNotFoundError:
        print("Certificados não encontrados, usando SSL adhoc")
        return 'adhoc'

if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    ssl_context = create_ssl_context()
    print(f"Servidor Flask iniciando em https://{host}:{port}")
    app.run(
        host=host,
        port=port,
        debug=True,
        threaded=True,
        use_reloader=False,
        ssl_context=ssl_context
    )
