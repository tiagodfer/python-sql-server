from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import os
import ssl
from argon2 import PasswordHasher
import datetime
import json


app = Flask(__name__)

USERS = {
    "admin@mail.com" : "admin123",
    "teste@mail.com" : "teste123"
}

# Configuração CORS
CORS(app, resources={
    r"/*": {
        "origins": ["https://localhost:3000", "http://localhost:3000", "https://127.0.0.1:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Origin", "Accept"],
        "supports_credentials": True
    }
})

# Configuração adicional para CORS
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['https://localhost:3000', 'http://localhost:3000', 'https://127.0.0.1:3000', 'http://127.0.0.1:3000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Origin', '*')

    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Origin,Accept')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')

    # Headers para debug
    print("Status:", response.status)
    print("Headers:", response.headers)
    print("Response data:", response.get_data(as_text=True))
    return response

# LOGIN

USER_SESSIONS = {}

def save_sessions_to_json():
    try:
        with open('user_sessions.json', 'w', encoding='utf-8') as f:
            json.dump(USER_SESSIONS, f, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        print(f"Erro ao salvar sessões: {e}")

# Rota Login
@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in USERS and USERS[username] == password:
        # Criar timestamp do login
        login_timestamp = datetime.datetime.now().isoformat()
        
        # Armazenar informações da sessão
        USER_SESSIONS[username] = {
            'username': username,
            'login_timestamp': login_timestamp,
        }
        
        # Salvar sessões no arquivo JSON
        save_sessions_to_json()
        
        return jsonify({
            "message": "Login successful!",
            "username": username,
            "login_timestamp": login_timestamp
        }), 200
    
    return jsonify({"message": "Invalid credentials"}), 401

# Rotas SQL
@app.route("/get-person-by-name/<name>", methods=['GET', 'OPTIONS'])
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
def get_person_cnpj_by_name(name, cpf):
    if request.method == 'OPTIONS':
        return '', 200

    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute("SELECT nome_socio, nome_representante, cnpj_cpf_socio FROM socios WHERE (nome_socio LIKE UPPER(?) OR nome_representante LIKE UPPER(?)) AND cnpj_cpf_socio LIKE ?", ('%' + name + '%', '%' + name + '%', '%' + cpf[3:-2] + '%'))
        results = cursor_cnpj.fetchall()
        conn_cnpj.close()

        if results:
            cnpj_list = []
            for row in results:
                cnpj_info = {
                    'nome fantasia': row[0],
                    'nome': row[1],
                    'cpf': row[2],
                }
                cnpj_list.append(cnpj_info)
            return jsonify({'results': cnpj_list}), 200
        else:
            return jsonify({'error': 'Nome não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-cnpj-person-by-cnpj/<cnpj>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_cpf(cnpj):
    if request.method == 'OPTIONS':
        return '', 200

    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute(
            "SELECT cnpj, nome_fantasia, uf FROM estabelecimento WHERE cnpj_basico = ?",
            (cnpj,)
        )
        results = cursor_cnpj.fetchall()

        cnpj_list = []
        for row in results:
            cnpj_basico = row[0]
            cursor_cnpj.execute(
                "SELECT nome_socio, nome_representante, cnpj_cpf_socio FROM socios WHERE cnpj_basico = ?",
                (cnpj_basico,)
            )
            socios = cursor_cnpj.fetchall()
            socios_list = [
                {
                    'nome_socio': s[0],
                    'nome_representante': s[1],
                    'cnpj_cpf_socio': s[2]
                }
                for s in socios
            ]
            cpf_info = {
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
        # Tenta usar certificado e chave existentes
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain('ssl/server.crt', 'ssl/server.key')
        return context
    except FileNotFoundError:
        # Se não encontrar certificados, usa adhoc
        print("Certificados não encontrados, usando SSL adhoc")
        return 'adhoc'

if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))

    # Configuração SSL
    ssl_context = create_ssl_context()

    print(f"Servidor Flask iniciando em https://{host}:{port}")
    print("Certificados SSL configurados")

    app.run(
        host=host, 
        port=port, 
        debug=True, 
        threaded=True, 
        use_reloader=False,
        ssl_context=ssl_context
    )
