from flask import Flask, jsonify, request
import sqlite3
from flask_cors import CORS
import os
import ssl

app = Flask(__name__)

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

@app.route("/get-person-cnpj-by-name/<name>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_name(name):
    if request.method == 'OPTIONS':
        return '', 200
        
    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute("SELECT * FROM socios WHERE nome LIKE UPPER(?)", ('%' + name + '%',))
        results = cursor_cnpj.fetchall()
        conn_cnpj.close()
        
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    'cpf': row[3],
                    'nome': row[2],
                }
                cpf_list.append(cpf_info)
            return jsonify({'results': cpf_list}), 200
        else:
            return jsonify({'error': 'Nome não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-person-cnpj-by-name-cpf/<name>-<cpf>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_cpf(name, cpf):
    if request.method == 'OPTIONS':
        return '', 200
        
    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute("SELECT * FROM socios WHERE representante_legal LIKE ? AND nome_representante LIKE ?", ('%' + cpf[3:9] + '%', '%' + name + '%',))
        results = cursor_cnpj.fetchall()
        conn_cnpj.close()
        
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    'nome fantasia': row[2],
                    'nome': row[8],
                    'cpf': row[7]
                }
                cpf_list.append(cpf_info)
            return jsonify({'results': cpf_list}), 200
        else:
            return jsonify({'error': 'Não é sócio de nenhuma empresa'}), 404
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route("/get-person-cnpj-by-name-cpf-radical/<name>-<cpf>", methods=['GET', 'OPTIONS'])
def get_person_cnpj_by_cpf_radical(name, cpf):
    if request.method == 'OPTIONS':
        return '', 200
        
    cnpj_db_path = os.environ.get('CNPJ_DB_PATH', 'db/cnpj.db')
    try:
        conn_cnpj = sqlite3.connect(cnpj_db_path)
        cursor_cnpj = conn_cnpj.cursor()
        cursor_cnpj.execute("SELECT * FROM socios WHERE cpf_cnpj LIKE ? AND nome LIKE ?", ('%' + cpf[3:9] + '%', '%' + name + '%',))
        results = cursor_cnpj.fetchall()
        
        if results:
            cpf_list = []
            for row in results:
                cpf_info = {
                    '0 - cpf': row[3],
                    '0 - nome': row[2],
                }
                cpf_list.append(cpf_info)
                cursor_cnpj.execute("SELECT * FROM estabelecimentos WHERE radical = ?", (row[0],))
                results_est = cursor_cnpj.fetchall()
                num_empresa = 0
                if results_est:
                    for row_est in results_est:
                        num_empresa += 1
                        key = f'{num_empresa} nome fantasia'
                        key2 = f'{num_empresa} rua'
                        key3 = f'{num_empresa} num'
                        key4 = f'{num_empresa} estado'
                        cpf_info[key] = row_est[4]
                        cpf_info[key2] = row_est[14]
                        cpf_info[key3] = row_est[15]
                        cpf_info[key4] = row_est[19]
            conn_cnpj.close()
            return jsonify({'results': cpf_list}), 200
        else:
            conn_cnpj.close()
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
