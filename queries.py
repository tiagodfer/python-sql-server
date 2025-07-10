import sqlite3
import json

def search_cpf_by_exact_name(name, cursor):
    name = name.upper()
    cursor.execute(
        "SELECT cpf, nome, sexo, nasc FROM cpf WHERE nome = ? COLLATE NOCASE",
        (name,)
    )
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
        }
        json_result.append(json_dict)
    return json_result

def search_cpf_by_name(name, cursor):
    name = name.upper()
    cursor.execute(
        "SELECT cpf, nome, sexo, nasc FROM cpf WHERE nome LIKE ?",
        ('%' + name + '%',)
    )
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
        }
        json_result.append(json_dict)
    return json_result

def search_cpf_by_cpf(cpf, cursor):
    cursor.execute(
        "SELECT cpf, nome, sexo, nasc FROM cpf WHERE cpf = ?",
        (cpf,)
    )
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
        }
        json_result.append(json_dict)
    return json_result

def check_person_cnpj(name, cursor):
    cursor.execute(
        "SELECT cpf_cnpj, nome, sexo, nasc FROM socios WHERE nome LIKE ?",
        ('%' + name + '%',)
    )
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1],
            'sexo': row[2],
            'nasc': row[3]
        }
        json_result.append(json_dict)
    return json_result

def check_person_cnpj_and_cpf(name_and_cpf, cursor):
    name = name_and_cpf[:-6]
    cpf = name_and_cpf[-6:]
    cursor.execute(
        "SELECT cpf_cnpj, nome FROM socios WHERE nome LIKE ? AND cpf_cnpj LIKE ?",
        (name, '%' + cpf + '%',)
    )
    result = cursor.fetchall()
    json_result = []
    for row in result:
        json_dict = {
            'cpf': row[0],
            'nome': row[1]
        }
        json_result.append(json_dict)
    return json_result
