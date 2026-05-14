from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def init_db():
    conn = sqlite3.connect('helpdesk.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL,
        tipo TEXT NOT NULL,
        descricao TEXT NOT NULL,
        status TEXT DEFAULT 'Novo',
        resposta TEXT DEFAULT '',
        data_abertura TEXT NOT NULL,
        data_fechamento TEXT DEFAULT ''
    )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/abrir', methods=['POST'])
def abrir_chamado():
    nome = request.form['nome']
    email = request.form['email']
    tipo = request.form['tipo']
    descricao = request.form['descricao']
    data = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    conn = sqlite3.connect('helpdesk.db')
    c = conn.cursor()
    c.execute('INSERT INTO tickets (nome, email, tipo, descricao, data_abertura) VALUES (?, ?, ?, ?, ?)',
              (nome, email, tipo, descricao, data))
    ticket_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return render_template('index.html', sucesso=True, protocolo=ticket_id)

@app.route('/admin')
def admin():
    if not session.get('logado'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('helpdesk.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets ORDER BY id DESC')
    tickets = c.fetchall()
    conn.close()
    
    return render_template('admin.html', tickets=tickets)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario == 'recrutador' and senha == 'helpdesk2026':
            session['logado'] = True
            return redirect(url_for('admin'))
        return render_template('login.html', erro=True)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/ticket/<int:ticket_id>')
def ver_ticket(ticket_id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('helpdesk.db')
    c = conn.cursor()
    c.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    ticket = c.fetchone()
    conn.close()
    
    return render_template('ticket.html', ticket=ticket)

@app.route('/atualizar/<int:ticket_id>', methods=['POST'])
def atualizar_ticket(ticket_id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    
    status = request.form['status']
    resposta = request.form['resposta']
    
    conn = sqlite3.connect('helpdesk.db')
    c = conn.cursor()
    
    if status == 'Resolvido':
        data_fechamento = datetime.now().strftime('%d/%m/%Y %H:%M')
        c.execute('UPDATE tickets SET status=?, resposta=?, data_fechamento=? WHERE id=?',
                  (status, resposta, data_fechamento, ticket_id))
    else:
        c.execute('UPDATE tickets SET status=?, resposta=? WHERE id=?',
                  (status, resposta, ticket_id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)