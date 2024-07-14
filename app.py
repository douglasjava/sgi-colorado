from flask import Flask, render_template, request, redirect, url_for, flash

import csv
from urllib.parse import parse_qs, urlparse

app = Flask(__name__)
app.secret_key = 'supersecretkey'


def load_names():
    nomes = []
    with open("nomes.csv", "r", encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            id, nome = row
            nomes.append({'id': id, 'nome': nome})
    return nomes


def load_result():
    result = []
    with open("presenca.csv", "r", encoding='UTF-8') as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            id, nome, grupo, data = row
            result.append({'id': id, 'nome': nome, "grupo": grupo, "data": data})
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chamada', methods=['GET', 'POST'])
def chamada():
    nomes = load_names()
    if request.method == 'POST':
        nome_id = request.form['nome']
        grupo = request.form['grupo']
        data = request.form['data']
        tipo = request.form['tipo']
        visitante = request.form['visitante']

        # Verifica se nome_id é "Selecione..."
        if nome_id == "Selecione...":
            # Se o campo visitante estiver vazio, retorna um erro
            if not visitante:
                flash('O campo membro ou vistante é obrigatório', 'error')
                return render_template('chamada.html', nomes=nomes)

            # Caso contrário, usa o nome do visitante
            nome = visitante
            id = "N/A"  # ID não é aplicável para visitantes
        else:
            # Divide o nome_id em id e nome_cadastrado
            id, nome_cadastrado = nome_id.split('|')
            nome = nome_cadastrado

        with open("presenca.csv", "a") as file:
            file.write(f"{id};{nome};{grupo};{data};{tipo}\n")

        return redirect(url_for('index'))
    return render_template('chamada.html', nomes=nomes)


@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    presencas = get_presenca()

    # Se a requisição for GET, obtém os filtros da query string da URL
    parsed_url = urlparse(request.url)
    parsed_params = parse_qs(parsed_url.query)
    grupo_filter = parsed_params.get('grupo', [''])[0]
    data_filter = parsed_params.get('data', [''])[0]

    print(f"Filtro aplicado: Grupo={grupo_filter}, Data={data_filter}")
    print(f"Presenças sem filtro: {presencas}")

    # Aplica os filtros se algum deles estiver preenchido
    presencas = [item for item in presencas if grupo_filter in item]
    presencas = [item for item in presencas if data_filter in item]

    print(f"Presenças filtradas: {presencas}")

    return render_template('pesquisa.html', presencas=presencas)


def get_presenca():
    with open("presenca.csv", "r", encoding='ISO-8859-1') as file:
        presencas = file.read().splitlines()
    return presencas


if __name__ == '__main__':
    app.run(debug=True)
