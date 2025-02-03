from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do banco de dados
db = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="certificado"
)

def execute_query(query, params=(), fetch=False, fetchone=False):
    # Cria um cursor para executar a consulta, configurado para retornar resultados como dicionários
    cursor = db.cursor(pymysql.cursors.DictCursor)
    
    # Executa a consulta SQL com os parâmetros fornecidos
    cursor.execute(query, params)
    
    # Verifica se deve buscar resultados da consulta
    if fetch:
        # Se 'fetchone' é True, retorna apenas o primeiro resultado
        if fetchone:
            result = cursor.fetchone()
        else:
            # Caso contrário, retorna todos os resultados
            result = cursor.fetchall()
        return result
    else:
        # Se 'fetch' é False, faz commit da transação (útil para operações de escrita)
        db.commit()

@app.route('/')
def index():
    # Executa uma consulta SQL para selecionar todos os participantes
    participants = execute_query("SELECT * FROM participants", fetch=True)
    # Renderiza o template 'index.html' com a lista de participantes
    return render_template('index.html', participants=participants)


@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    # Verifica se o método da requisição é POST
    if request.method == 'POST':
        # Obtém os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form.get('data_nascimento')
        # Cria a consulta SQL para inserir um novo participante
        sql = "INSERT INTO participants (nome, cpf, data_nascimento) VALUES (%s, %s, %s)"
        # Executa a consulta para inserir o novo participante
        execute_query(sql, (nome, cpf, data_nascimento))
        # Redireciona para a página principal após a inserção
        return redirect(url_for('index'))
    # Renderiza o template 'add_participant.html' se o método for GET
    return render_template('add_participant.html')


@app.route('/update_participant/<int:id>', methods=['GET', 'POST'])
def update_participant(id):
    # Verifica se o método da requisição é POST
    if request.method == 'POST':
        # Obtém os dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form.get('data_nascimento')
        # Cria a consulta SQL para atualizar o participante
        sql = "UPDATE participants SET nome = %s, cpf = %s, data_nascimento = %s WHERE id = %s"
        # Executa a consulta para atualizar o participante
        execute_query(sql, (nome, cpf, data_nascimento, id))
        # Redireciona para a página principal após a atualização
        return redirect(url_for('index'))
    
    # Executa a consulta SQL para obter os dados do participante
    participant = execute_query("SELECT * FROM participants WHERE id = %s", (id,), fetch=True, fetchone=True)
    # Renderiza o template 'update_participant.html' com os dados do participante
    return render_template('update_participant.html', participant=participant)


@app.route('/delete_participant/<int:id>', methods=['POST'])
def delete_participant(id):
    # Cria a consulta SQL para deletar o participante
    sql = "DELETE FROM participants WHERE id = %s"
    # Executa a consulta para deletar o participante
    execute_query(sql, (id,))
    # Redireciona para a página principal após a deleção
    return redirect(url_for('index'))


@app.route('/select_participants', methods=['GET', 'POST'])
def select_participants():
    # Verifica se o método da requisição é POST
    if request.method == 'POST':
        # Obtém a lista de IDs dos participantes selecionados no formulário
        participant_ids = request.form.getlist('participants')
        # Obtém o tipo de certificado selecionado no formulário
        certificate_type = request.form['certificate_type']
        # Obtém a data selecionada no formulário
        date = request.form['date']
        # Formata a data para o formato brasileiro (dd/mm/yyyy)
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')  
        # Obtém a carga horária selecionada no formulário
        hours = request.form['hours']
        # Obtém o local selecionado no formulário
        location = request.form['location']
        
        # Consulta SQL para selecionar os participantes com base nos IDs selecionados
        sql = "SELECT * FROM participants WHERE id IN ({})".format(','.join(['%s'] * len(participant_ids)))
        # Executa a consulta e obtém os participantes selecionados
        participants = execute_query(sql, participant_ids, fetch=True)
        
        # Cria uma lista de dados para os certificados a serem gerados
        data_list = [{
            'certificate_type': certificate_type,
            'participant_name': participant['nome'],
            'participant_cpf': participant['cpf'],
            'hours': hours,
            'date': formatted_date,
            'location': location
        } for participant in participants]
        
        # Renderiza o template 'multiple_certificates.html' com a lista de dados dos certificados
        return render_template('multiple_certificates.html', data_list=data_list)
    
    # Se o método da requisição é GET, executa a consulta para obter todos os participantes
    participants = execute_query("SELECT * FROM participants", fetch=True)
    # Renderiza o template 'select_participants.html' com a lista de participantes
    return render_template('select_participants.html', participants=participants)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
