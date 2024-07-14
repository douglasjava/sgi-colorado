import sqlite3
import csv


class DatabaseManager:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.create_db_pessoa()
        self.create_db_presenca()

    def create_db_presenca(self):
        conn = sqlite3.connect(self.db_name)
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

    def create_db_pessoa(self):
        conn = sqlite3.connect(self.db_name)
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

    def insert_nome(self, nome, situacao, grupo, categoria):
        conn = sqlite3.connect(self.db_name)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO pessoa (nome, situacao, grupo, categoria)
            VALUES (?, ?, ?, ?)
        ''', (nome, situacao, grupo, categoria))
        conn.commit()
        conn.close()

    def insert_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='UTF-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                nome, situacao, grupo, categoria = row
                self.insert_nome(nome, situacao, grupo, categoria)
