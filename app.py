import os
import sqlite3
from io import StringIO

from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify

import csv
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)
app.secret_key = 'supersecretkey'


def load_names():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute('SELECT * FROM pessoa')
    pessoas = cur.fetchall()
    conn.close()
    return pessoas


def load_result(grupo_filter=None, data_filter=None):
    conn = sqlite3.connect('database.db')
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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chamada', methods=['GET', 'POST'])
def chamada():
    pessoas = load_names()
    if request.method == 'POST':
        ids = request.form.getlist('nome')
        data = request.form['data']
        tipo = request.form['tipo']
        visitante = request.form['visitante']

        # Verifica se o campo visitante está vazio e nenhum membro foi selecionado
        if not ids and not visitante:
            flash('O campo membro ou visitante é obrigatório', 'error')
            return render_template('chamada.html', nomes=pessoas)

        if tipo == "Selecione...":
            flash('O campo tipo é obrigatório', 'error')
            return render_template('chamada.html', nomes=pessoas)

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        if ids:
            for id in ids:
                cur.execute('''
                    INSERT INTO presenca (pessoa_id, data, tipo)
                    VALUES (?, ?, ?)
                ''', (id, data, tipo))

        # Adiciona o visitante se foi preenchido
        if visitante:
            cur.execute('''
                INSERT INTO presenca (nome_visitante, data, tipo)
                VALUES (?, ?, ?)
            ''', (visitante, data, tipo))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('chamada.html', nomes=pessoas)


@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    parsed_url = urlparse(request.url)
    parsed_params = parse_qs(parsed_url.query)
    grupo_filter = parsed_params.get('grupo', [''])[0]
    data_filter = parsed_params.get('data', [''])[0]

    print(f"Filtro aplicado: Grupo={grupo_filter}, Data={data_filter}")

    # Carrega os resultados com os filtros aplicados
    presencas = load_result(grupo_filter, data_filter)

    for presenca in presencas:
        print(dict(presenca))

    return render_template('pesquisa.html', presencas=presencas)


# Rota para fazer o download do arquivo CSV
@app.route('/download_csv')
def download_csv():
    presencas = load_result()

    # Cria um arquivo CSV em memória
    output = StringIO()
    csv_writer = csv.writer(output)

    # Escreve os dados das presenças no arquivo CSV
    csv_writer.writerow(['ID', 'Nome', 'Grupo', 'Data', 'Tipo'])
    for presenca in presencas:
        csv_writer.writerow([presenca['id'], presenca['nome'], presenca['grupo'], presenca['data'], presenca['tipo']])

    # Retorna o arquivo CSV como uma resposta para download
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=lista_presenca.csv"}
    )


@app.route('/dashboard', methods=['GET'])
def dashboard():
    presencas = load_result()

    presencasJson = [dict(row) for row in presencas]

    return render_template('dashboard.html', presencas=presencasJson)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
