import os
import psycopg2
import psycopg2.extras
import csv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, '../data')
DATABASE_URL = os.environ.get('DATABASE_URL',
                              'postgres://ue43jbcd11q1dj:pb84d8471a74cb5095b464cc831c7309c2031d5d3fee8d853f6b4ff067bbdd5cc@c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/driss6kr58v7a')


def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)


def create_db_pessoa():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pessoa (
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
            pessoa_id INTEGER,
            nome_visitante TEXT,
            data DATE,
            tipo TEXT,
            FOREIGN KEY (pessoa_id) REFERENCES pessoa (id)
        )
    ''')
    conn.commit()
    conn.close()


def load_names():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pessoa')
    pessoas = cur.fetchall()
    conn.close()
    return pessoas


def load_result(grupo_filter=None, data_filter=None, visitante_filter=None, tipo_filter=None, data_filter_fim=None):
    conn = get_connection()
    cur = conn.cursor()

    query = '''
          SELECT 
              p1.id, 
              p1.pessoa_id, 
              p1.nome_visitante, 
              p1.data, 
              p1.tipo,
              p2.id AS pessoa_id, 
              p2.nome, 
              p2.situacao, 
              p2.grupo, 
              p2.categoria
          FROM presenca p1 
          LEFT JOIN pessoa p2 ON p1.pessoa_id = p2.id 
          WHERE 1=1
      '''
    params = []

    if grupo_filter:
        query += ' AND grupo = %s'
        params.append(grupo_filter)

    if data_filter and data_filter_fim:
        query += ' AND data BETWEEN %s AND %s'
        params.extend([data_filter, data_filter_fim])
    elif data_filter:
        query += ' AND data >= %s'
        params.append(data_filter)
    elif data_filter_fim:
        pass

    if tipo_filter:
        query += ' AND tipo = %s'
        params.append(tipo_filter)

    if visitante_filter == 'SIM':
        query += ' AND pessoa_id IS NULL'

    if visitante_filter == 'NAO':
        query += ' AND pessoa_id IS NOT NULL'

    cur.execute(query, params)
    presenca = cur.fetchall()
    conn.close()
    return presenca


def insert_nome(nome, situacao, grupo, categoria):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO pessoa (nome, situacao, grupo, categoria)
        VALUES (%s, %s, %s, %s)
    ''', (nome, situacao, grupo, categoria))
    conn.commit()
    conn.close()

def remover_chamada(presenca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM presenca WHERE id = %s", (presenca_id,))
    conn.commit()
    conn.close()


def count_pessoa_grupo():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(''' 
        SELECT grupo, COUNT(*) as total
        FROM pessoa
        WHERE grupo IN ('GRUPO A', 'GRUPO B', 'GRUPO C', 'GRUPO D', 'GRUPO E')
        GROUP BY grupo;
    ''')

    count_group = cur.fetchall()
    conn.close()

    group_counts = {row['grupo']: row['total'] for row in count_group}

    return group_counts


def count_pessoa():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''SELECT COUNT(*) FROM pessoa''')
    count = cur.fetchone()['count']
    conn.close()
    return count


def insert_presenca(pessoa_id=None, nome_visitante=None, data=None, tipo=None):
    conn = get_connection()
    cur = conn.cursor()

    # Verifica se a presenca já existe para pessoa_id
    if pessoa_id:
        cur.execute('''
            SELECT COUNT(*) FROM presenca 
            WHERE pessoa_id = %s AND data = %s AND tipo = %s
        ''', (pessoa_id, data, tipo))
        count = cur.fetchone()['count']
        if count == 0:
            cur.execute('''
                INSERT INTO presenca (pessoa_id, data, tipo)
                VALUES (%s, %s, %s)
            ''', (pessoa_id, data, tipo))

    # Verifica se a presenca já existe para nome_visitante
    if nome_visitante:
        cur.execute('''
            SELECT COUNT(*) FROM presenca 
            WHERE nome_visitante = %s AND data = %s AND tipo = %s
        ''', (nome_visitante, data, tipo))
        count = cur.fetchone()['count']
        if count == 0:
            cur.execute('''
                INSERT INTO presenca (nome_visitante, data, tipo)
                VALUES (%s, %s, %s)
            ''', (nome_visitante, data, tipo))

    conn.commit()
    conn.close()


def insert_from_csv(csv_file):
    with open(csv_file, 'r', encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            nome, situacao, grupo, categoria = row
            insert_nome(nome, situacao, grupo, categoria)


def insert_item_event_tf(visitor_name, phone, responsible, event_date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO public.trombetas_festas(visitor_name, phone, responsible, event_date)
        VALUES (%s, %s, %s, %s);
    ''', (visitor_name, phone, responsible, event_date))  # Corrigido para passar as variáveis
    conn.commit()
    conn.close()

def pesquisa_event_tf():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM public.trombetas_festas')
    visitantes = cur.fetchall()
    conn.close()

    return visitantes


class DatabaseManager:
    def __init__(self, db_name=DATABASE_URL):
        self.db_name = db_name
        create_db_pessoa()
        create_db_presenca()