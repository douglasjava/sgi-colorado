import os
from datetime import datetime
from io import StringIO
import unicodedata

from flask import Flask, render_template, request, redirect, url_for, flash, Response, session

import csv
from urllib.parse import parse_qs, urlparse

from database.database_manager import load_names, insert_presenca, load_result, remover_chamada, count_pessoa_grupo, \
    count_pessoa, insert_item_event_tf, pesquisa_event_tf

app = Flask(__name__)
app.secret_key = 'supersecretkey'

DAYS_MAP = {
    0: 'Segunda',
    1: 'Terca',
    2: 'Quarta',
    3: 'Quinta',
    4: 'Sexta',
    5: 'Sábado',
    6: 'Domingo'
}

@app.route('/')
def index():
    data_filter = session.get('data_filter', None)
    tipo_filter = session.get('tipo_filter', None)

    presencas = load_result(data_filter=data_filter, tipo_filter=tipo_filter)
    countGroup = count_pessoa_grupo()
    total_registrado = count_pessoa()

    presencasJson = [dict(row) for row in presencas]

    presence_percentage = calculate_presence_percentage(presencas, countGroup)
    totalPresenca = len(presencas)

    for presenca in presencas:
        print(dict(presenca))
    print(countGroup)
    print(total_registrado)
    print(totalPresenca)

    return render_template('index.html', presencas=presencasJson, porcentage=presence_percentage, totalPresenca=totalPresenca, total_registrado=total_registrado)


@app.route('/buscar', methods=['GET'])
def buscar_presencas():
    data = request.args.get('data')
    tipo = request.args.get('tipo')

    # Armazena a data escolhida na sessão
    session['data_filter'] = data
    session['tipo_filter'] = tipo

    # Redireciona de volta para a página principal
    return redirect(url_for('index'))


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

        if ids:
            for id in ids:
                insert_presenca(pessoa_id=id, data=data, tipo=tipo)

        if visitante:
            visitantes = [v.strip().upper() for v in visitante.split(',')] if ',' in visitante else [visitante.strip().upper()]
            for nome_visitante in visitantes:
                insert_presenca(nome_visitante=nome_visitante, data=data, tipo=tipo)

        return redirect(url_for('index'))
    return render_template('chamada.html', nomes=pessoas)


@app.route('/pesquisa', methods=['GET', 'POST'])
def pesquisa():
    parsed_url = urlparse(request.url)
    parsed_params = parse_qs(parsed_url.query)
    grupo_filter = parsed_params.get('grupo', [''])[0]
    data_filter = parsed_params.get('data', [''])[0]
    visitante_filter = parsed_params.get('visitante', [''])[0]
    tipo_filter = parsed_params.get('tipo', [''])[0]

    print(f"Filtro aplicado: Filtros={parsed_params}")

    # Carrega os resultados com os filtros aplicados
    presencas = load_result(grupo_filter, data_filter, visitante_filter, tipo_filter)

    count_visitante_Registrado = sum(1 for presenca in presencas if presenca['situacao'] == 'Visitante')
    count_visitante_Frequente = sum(1 for presenca in presencas if presenca['situacao'] == 'Visitante Frequente')
    count_visitante = sum(1 for item in presencas if item['nome_visitante'] is not None)
    count_membro = sum(1 for item in presencas if item['situacao'] == 'Membro')
    count_membro_nao_batizado = sum(1 for item in presencas if item['situacao'] == 'Membro não batizado')
    count_cias_1 = sum(1 for item in presencas if item['categoria'] == 'Adolescente')
    count_cias_2 = sum(1 for item in presencas if item['categoria'] == 'Criança (Intermediário) 7-11')
    count_cias_3 = sum(1 for item in presencas if item['categoria'] == 'Criança (Pequeno) 3-7')
    count_cias_4 = sum(1 for item in presencas if item['categoria'] == 'Criança de Colo 0-3')

    count_visitante_total = count_visitante + count_visitante_Registrado + count_visitante_Frequente
    count_membros_total = count_membro + count_membro_nao_batizado
    count_cias_total = count_cias_1 + count_cias_2 + count_cias_3 + count_cias_4;

    for presenca in presencas:
        print(dict(presenca))

    return render_template('pesquisa.html', presencas=presencas, count_visitante=count_visitante_total, count_membro=count_membros_total, count_cias=count_cias_total)


@app.route('/download_csv')
def download_csv():

    # Captura os parâmetros de filtro da URL
    grupo_filter = request.args.get('grupo', '')
    data_filter = request.args.get('data', '')
    visitante_filter = request.args.get('visitante', '')
    tipo_filter = request.args.get('tipo', '')

    # Carrega os resultados com os filtros aplicados
    presencas = load_result(grupo_filter, data_filter, visitante_filter, tipo_filter)

    # Cria um arquivo CSV em memória
    output = StringIO()
    csv_writer = csv.writer(output)

    # Escreve os dados das presenças no arquivo CSV
    csv_writer.writerow(['ID', 'Nome', 'Grupo', 'Data', 'Tipo'])
    for presenca in presencas:
        nome = presenca['nome_visitante'] or presenca['nome']
        csv_writer.writerow([presenca['id'], nome, presenca['grupo'], presenca['data'], presenca['tipo']])

    # Retorna o arquivo CSV como uma resposta para download
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=lista_presenca.csv"}
    )


@app.route('/download_tf_csv')
def download_tf_csv():
    try:
        # Recupera os dados dos visitantes
        visitantes = pesquisa_event_tf()

        # Cria um arquivo CSV na memória
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=['Nome do Visitante', 'Telefone', 'Responsavel', 'Data do Evento'])
        writer.writeheader()

        for visitante in visitantes:
            writer.writerow({
                'Nome do Visitante': visitante['visitor_name'],
                'Telefone': visitante['phone'],
                'Responsavel': visitante['responsible'],
                'Data do Evento': visitante['event_date'].strftime('%Y-%m-%d')  # Formata a data
            })

        # Rewind no StringIO
        output.seek(0)

        # Retorna a resposta com o CSV gerado
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment;filename=visitantes.csv"}
        )

    except Exception as e:
        print(f"Erro ao gerar o arquivo CSV: {e}")
        flash("Erro ao gerar o arquivo CSV.", 'danger')
        return redirect('/pesquisa_trombetas')


@app.route('/dashboard', methods=['GET'])
def dashboard():

    presencas = load_result()

    presencasJson = [dict(row) for row in presencas]

    return render_template('dashboard.html', presencas=presencasJson)


@app.route('/delete_presenca/<int:presenca_id>', methods=['POST'])
def delete_presenca(presenca_id):
    remover_chamada(presenca_id)
    flash('Registro excluído com sucesso!', 'success')
    return redirect(url_for('pesquisa'))


def remover_acentos(texto):
    return ''.join(
        char for char in unicodedata.normalize('NFD', texto)
        if unicodedata.category(char) != 'Mn'
    )

@app.route('/trombetas', methods=['GET', 'POST'])
def trombetas():
    if request.method == 'GET':
        list_people = load_names()
        lista_de_pessoas = [remover_acentos(people['nome']) for people in list_people]
        return render_template('trombetas.html', lista_de_pessoas=lista_de_pessoas)

    if request.method == 'POST':
        try:
            visitantes = request.json.get('visitantes', [])
            data_register = datetime.now().strftime('%Y-%m-%d')

            if not visitantes:
                flash('Nenhum dado recebido!', 'danger')
                return redirect('/trombetas')

            for visitante in visitantes:
                insert_item_event_tf(
                    visitante['name'],
                    visitante['phone'],
                    visitante['responsible'],
                    data_register
                )

            flash('Visitantes registrados com sucesso!', 'success')
        except Exception as e:
            print(f"Erro ao registrar os visitantes: ", e)
            flash(f'Ocorreu um erro ao registrar os visitantes: {str(e)}', 'danger')

        return redirect('/trombetas')


@app.route('/pesquisa_trombetas', methods=['GET'])
def pesquisa_trombetas():
    try:

        visitantes = pesquisa_event_tf()

        # Passa os dados para o template
        return render_template('pesquisa_trombetas.html', visitantes=visitantes)

    except Exception as e:
        print(f"Erro ao consultar dados: {e}")
        flash("Erro ao carregar os dados.", 'danger')
        return redirect('/pesquisa_trombetas')


def calculate_presence_percentage(presencas, count_group):
    presence_count = {'GRUPO A': 0, 'GRUPO B': 0, 'GRUPO C': 0, 'GRUPO D': 0}

    # Conta as presenças de cada grupo
    for presenca in presencas:
        grupo = presenca['grupo']
        if grupo in presence_count:
            presence_count[grupo] += 1

    # Calcula a porcentagem de cada grupo
    presence_percentage = {}
    for grupo, total in count_group.items():
        if total > 0:
            presence_percentage[grupo] = (presence_count[grupo] / total) * 100
        else:
            presence_percentage[grupo] = 0

    formatted_data = format_percentage(presence_percentage)

    return formatted_data


def format_percentage(data):
    formatted_data = {}
    for grupo, value in data.items():
        formatted_data[grupo] = f"{value:.2f}"
    return formatted_data


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
