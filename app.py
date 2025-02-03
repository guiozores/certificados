from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import pymysql
import re  # Para manipularmos os dígitos do CPF

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuração do banco de dados
db = pymysql.connect(
    host="localhost",
    user="guiozores",
    password="q1w2e3r4",
    database="certificado"
)

def execute_query(query, params=(), fetch=False, fetchone=False):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    if fetch:
        if fetchone:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()
        return result
    else:
        db.commit()

# Função para formatar CPF no padrão XXX.XXX.XXX-XX e garantir 11 dígitos
def format_cpf(cpf_str):
    # Remove qualquer caractere que não seja dígito (pontos, traços, espaços, etc.)
    digits = re.sub(r'\D', '', cpf_str)
    
    # Se tiver exatamente 11 dígitos, formata no padrão
    if len(digits) == 11:
        return f'{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}'
    else:
        # Se não tiver 11 dígitos, retornamos None (indicando erro)
        return None

@app.route('/')
def index():
    participants = execute_query("SELECT * FROM participants", fetch=True)
    return render_template('index.html', participants=participants)

@app.route('/add_participant', methods=['GET', 'POST'])
def add_participant():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form.get('data_nascimento')

        # Formata/valida o CPF antes de salvar
        cpf_formatado = format_cpf(cpf)
        if not cpf_formatado:
            flash("CPF inválido! É necessário ter exatamente 11 dígitos numéricos.")
            return redirect(url_for('add_participant'))

        sql = "INSERT INTO participants (nome, cpf, data_nascimento) VALUES (%s, %s, %s)"
        execute_query(sql, (nome, cpf_formatado, data_nascimento))
        return redirect(url_for('index'))

    return render_template('add_participant.html')

@app.route('/update_participant/<int:id>', methods=['GET', 'POST'])
def update_participant(id):
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form.get('data_nascimento')

        # Formata/valida o CPF antes de atualizar
        cpf_formatado = format_cpf(cpf)
        if not cpf_formatado:
            flash("CPF inválido! É necessário ter exatamente 11 dígitos numéricos.")
            return redirect(url_for('update_participant', id=id))

        sql = "UPDATE participants SET nome = %s, cpf = %s, data_nascimento = %s WHERE id = %s"
        execute_query(sql, (nome, cpf_formatado, data_nascimento, id))
        return redirect(url_for('index'))
    
    participant = execute_query("SELECT * FROM participants WHERE id = %s", (id,), fetch=True, fetchone=True)
    return render_template('update_participant.html', participant=participant)

@app.route('/delete_participant/<int:id>', methods=['POST'])
def delete_participant(id):
    sql = "DELETE FROM participants WHERE id = %s"
    execute_query(sql, (id,))
    return redirect(url_for('index'))

@app.route('/select_participants', methods=['GET', 'POST'])
def select_participants():
    if request.method == 'POST':
        participant_ids = request.form.getlist('participants')
        certificate_type = request.form['certificate_type']
        date = request.form['date']
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        hours = request.form['hours']
        location = request.form['location']
        
        sql = "SELECT * FROM participants WHERE id IN ({})".format(','.join(['%s'] * len(participant_ids)))
        participants = execute_query(sql, participant_ids, fetch=True)
        
        data_list = [{
            'certificate_type': certificate_type,
            'participant_name': participant['nome'],
            'participant_cpf': participant['cpf'],
            'hours': hours,
            'date': formatted_date,
            'location': location
        } for participant in participants]
        
        return render_template('multiple_certificates.html', data_list=data_list)
    
    participants = execute_query("SELECT * FROM participants", fetch=True)
    return render_template('select_participants.html', participants=participants)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
