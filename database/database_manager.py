import os
import sqlite3
import csv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, '../data')
DATABASE_URL = os.environ.get('DATABASE_URL', os.path.join(DATABASE_DIR, 'database_prd.db'))


def get_connection():
    return sqlite3.connect(DATABASE_URL)


def create_db_pessoa():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pessoa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            situacao TEXT NOT NULL,
            grupo TEXT NOT NULL,
            categoria TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def create_db_presenca():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS presenca (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pessoa_id INTEGER,
            nome_visitante TEXT,
            data TEXT,
            tipo TEXT,
            FOREIGN KEY (pessoa_id) REFERENCES pessoa (id)
        )
    ''')
    conn.commit()
    conn.close()


def load_names():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM pessoa')
    pessoas = cur.fetchall()
    conn.close()
    return pessoas


def load_result(grupo_filter=None, data_filter=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    query = 'SELECT * FROM presenca p1 INNER JOIN pessoa p2 on p1.pessoa_id = p2.id WHERE 1=1'
    params = []

    if grupo_filter:
        query += ' AND grupo = ?'
        params.append(grupo_filter)

    if data_filter:
        query += ' AND data = ?'
        params.append(data_filter)

    cur.execute(query, params)
    presenca = cur.fetchall()
    conn.close()
    return presenca


def insert_nome(nome, situacao, grupo, categoria):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO pessoa (nome, situacao, grupo, categoria)
        VALUES (?, ?, ?, ?)
    ''', (nome, situacao, grupo, categoria))
    conn.commit()
    conn.close()


def insert_presenca(pessoa_id=None, nome_visitante=None, data=None, tipo=None):
    conn = get_connection()
    cur = conn.cursor()

    # Verifica se a presenca já existe para pessoa_id
    if pessoa_id:
        cur.execute('''
            SELECT COUNT(*) FROM presenca 
            WHERE pessoa_id = ? AND data = ? AND tipo = ?
        ''', (pessoa_id, data, tipo))
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute('''
                INSERT INTO presenca (pessoa_id, data, tipo)
                VALUES (?, ?, ?)
            ''', (pessoa_id, data, tipo))

    # Verifica se a presenca já existe para nome_visitante
    if nome_visitante:
        cur.execute('''
            SELECT COUNT(*) FROM presenca 
            WHERE nome_visitante = ? AND data = ? AND tipo = ?
        ''', (nome_visitante, data, tipo))
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute('''
                INSERT INTO presenca (nome_visitante, data, tipo)
                VALUES (?, ?, ?)
            ''', (nome_visitante, data, tipo))

    conn.commit()
    conn.close()


def insert_from_csv(csv_file):
    with open(csv_file, 'r', encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            nome, situacao, grupo, categoria = row
            insert_nome(nome, situacao, grupo, categoria)


class DatabaseManager:
    def __init__(self, db_name=DATABASE_URL):
        self.db_name = db_name
        create_db_pessoa()
        create_db_presenca()
