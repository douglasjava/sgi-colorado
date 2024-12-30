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

def insert_or_update_from_csv(csv_file):

    conn = get_connection()
    cur = conn.cursor()

    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            nome, situacao, grupo, categoria = row

            cur.execute("SELECT id FROM pessoa WHERE nome = %s", (nome,))
            result = cur.fetchone()

            if result:
                pessoa_id = result['id']
                cur.execute(
                    """
                    UPDATE pessoa
                    SET situacao = %s, grupo = %s, categoria = %s
                    WHERE id = %s
                    """,
                    (situacao, grupo, categoria, pessoa_id)
                )
                print(f"Atualizado: {nome}")
            else:
                cur.execute(
                    """
                    INSERT INTO pessoa (nome, situacao, grupo, categoria)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nome, situacao, grupo, categoria)
                )
                print(f"Inserido: {nome}")

    conn.commit()
    cur.close()
    conn.close()
    print("Processamento concluído com sucesso!")


def main():
    csv_file = '../data/base.csv'  # Nome do arquivo CSV
    insert_or_update_from_csv(csv_file)


if __name__ == "__main__":
    main()