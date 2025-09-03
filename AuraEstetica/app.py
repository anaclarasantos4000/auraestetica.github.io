# IMPORTAÇÕES E CONFIGS
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from xhtml2pdf import pisa
from io import BytesIO
from datetime import date, datetime, timedelta
import os
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'

# Caminho do banco SQLite
caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'aura.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + caminho
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa o banco
db = SQLAlchemy(app)

# Configuração do e-mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gestaoauraestetica@gmail.com'
app.config['MAIL_PASSWORD'] = 'bwoo suih gfte uvir'
app.config['MAIL_DEFAULT_SENDER'] = ('Aura Estética', 'gestaoauraestetica@gmail.com')
mail = Mail(app)

# Scheduler para lembretes automáticos
scheduler = BackgroundScheduler()
scheduler.start()

# ======================
# MODELOS DO BANCO
# ======================

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)

class Procedimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.Text, nullable=True)

class Profissional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    numero_registro = db.Column(db.String(20), nullable=False)
    tipo_registro = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    especialidade = db.Column(db.String(100), nullable=False)

class Agendamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    procedimento_id = db.Column(db.Integer, db.ForeignKey('procedimento.id'), nullable=False)
    tipo_consulta = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey('profissional.id'), nullable=False)
    data = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default='Pendente')

    cliente = db.relationship('Cliente', backref='agendamentos')
    procedimento = db.relationship('Procedimento', backref='agendamentos')
    profissional = db.relationship('Profissional', backref='agendamentos')

# Cria as tabelas no banco
with app.app_context():
    db.create_all()

# ======================
# FUNÇÕES AUXILIARES
# ======================

def enviar_email_confirmacao(agendamento):
    """Envia e-mail confirmando agendamento."""
    msg = Message(
        subject="Confirmação de Agendamento - Aura Estética",
        recipients=[agendamento.cliente.email],
        body=(
            f"Olá {agendamento.cliente.nome},\n\n"
            f"Seu agendamento para {agendamento.procedimento.nome} "
            f"com {agendamento.profissional.nome} foi registrado.\n"
            f"Data: {agendamento.data} às {agendamento.hora}\n\n"
            "Atenciosamente,\nAura Estética"
        )
    )
    try:
        mail.send(msg)
        print(f"E-mail enviado para {agendamento.cliente.email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")

def agendar_lembrete(agendamento):
    """Agenda lembrete por e-mail 1 hora antes."""
    try:
        data_hora = datetime.strptime(f"{agendamento.data} {agendamento.hora}", "%Y-%m-%d %H:%M")
        horario_lembrete = data_hora - timedelta(hours=1)

        def enviar_lembrete():
            msg = Message(
                subject="Lembrete do seu agendamento - Aura Estética",
                recipients=[agendamento.cliente.email],
                body=(
                    f"Olá {agendamento.cliente.nome},\n\n"
                    f"Lembrete: você tem um agendamento para {agendamento.procedimento.nome} "
                    f"em {agendamento.data} às {agendamento.hora}.\n\n"
                    "Atenciosamente,\nAura Estética"
                )
            )
            try:
                mail.send(msg)
                print(f"Lembrete enviado para {agendamento.cliente.email}")
            except Exception as e:
                print(f"Erro ao enviar lembrete: {e}")

        scheduler.add_job(enviar_lembrete, 'date', run_date=horario_lembrete)
    except Exception as e:
        print(f"Erro ao agendar lembrete: {e}")

# ======================
# ROTAS DO SISTEMA
# ======================

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route("/dashboard")
def dashboard():
    hoje = date.today().strftime("%Y-%m-%d")
    return render_template(
        "index.html",
        total_clientes=Cliente.query.count(),
        total_procedimentos=Procedimento.query.count(),
        agendamentos_hoje=Agendamento.query.filter_by(data=hoje).all()
    )

# --- CLIENTES
@app.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'POST':
        novo = Cliente(
            nome=request.form['nome'],
            telefone=request.form['telefone'],
            email=request.form['email'],
            data_nascimento=request.form['data_nascimento']
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('clientes'))

    return render_template('clientes.html', clientes=Cliente.query.all(), cliente_em_edicao=None)

@app.route('/clientes/editar/<int:id>', methods=['POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template('clientes.html', clientes=Cliente.query.all(), cliente_em_edicao=cliente)

@app.route('/clientes/atualizar/<int:id>', methods=['POST'])
def atualizar_cliente(id):
    c = Cliente.query.get_or_404(id)
    c.nome = request.form['nome']
    c.telefone = request.form['telefone']
    c.email = request.form['email']
    c.data_nascimento = request.form['data_nascimento']
    db.session.commit()
    return redirect(url_for('clientes'))

@app.route('/clientes/excluir/<int:id>', methods=["POST"])
def excluir_cliente(id):
    db.session.delete(Cliente.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for("clientes"))

# --- PROFISSIONAIS
@app.route('/profissionais', methods=['GET', 'POST'])
def profissionais():
    if request.method == 'POST':
        novo = Profissional(
            nome=request.form['nome'],
            cpf=request.form['cpf'],
            numero_registro=request.form['numero_registro'],
            tipo_registro=request.form['tipo_registro'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            especialidade=request.form['especialidade']
        )
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('profissionais'))

    return render_template('profissionais.html', profissionais=Profissional.query.all(), profissional_em_edicao=None)

@app.route('/profissionais/editar/<int:id>', methods=['POST'])
def editar_profissional(id):
    prof = Profissional.query.get_or_404(id)
    return render_template('profissionais.html', profissionais=Profissional.query.all(), profissional_em_edicao=prof)

@app.route('/profissionais/atualizar/<int:id>', methods=['POST'])
def atualizar_profissional(id):
    p = Profissional.query.get_or_404(id)
    p.nome = request.form['nome']
    p.cpf = request.form['cpf']
    p.numero_registro = request.form['numero_registro']
    p.tipo_registro = request.form['tipo_registro']
    p.email = request.form['email']
    p.telefone = request.form['telefone']
    p.especialidade = request.form['especialidade']
    db.session.commit()
    return redirect(url_for('profissionais'))

@app.route('/profissionais/excluir/<int:id>', methods=['POST'])
def excluir_profissional(id):
    db.session.delete(Profissional.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('profissionais'))

# --- PROCEDIMENTOS
@app.route('/procedimentos', methods=['GET', 'POST'])
def procedimentos():
    procedimento_edit = None
    if request.method == 'POST':
        id_edit = request.form.get('id')
        if id_edit:
            p = Procedimento.query.get(id_edit)
            p.nome = request.form['nome']
            p.preco = request.form['preco']
            p.descricao = request.form.get('descricao', '')
        else:
            db.session.add(Procedimento(
                nome=request.form['nome'],
                preco=request.form['preco'],
                descricao=request.form.get('descricao', '')
            ))
        db.session.commit()
        return redirect(url_for('procedimentos'))

    return render_template('procedimentos.html', procedimentos=Procedimento.query.all(), procedimento_edit=procedimento_edit)

@app.route('/editar_procedimento/<int:id>')
def editar_procedimento(id):
    return render_template(
        'procedimentos.html',
        procedimentos=Procedimento.query.all(),
        procedimento_edit=Procedimento.query.get_or_404(id)
    )

@app.route('/procedimentos/excluir/<int:id>', methods=['POST'])
def excluir_procedimento(id):
    db.session.delete(Procedimento.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('procedimentos'))

# --- AGENDAMENTOS
@app.route('/agendamentos', methods=['GET', 'POST'])
def agendamentos():
    clientes = Cliente.query.all()
    procedimentos = Procedimento.query.all()
    profissionais = Profissional.query.all()
    agendamento_edit = None

    if request.method == 'POST':
        id = request.form.get('id')
        ag = Agendamento.query.get(id) if id else Agendamento()
        ag.cliente_id = request.form['cliente']
        ag.procedimento_id = request.form['procedimento']
        ag.tipo_consulta = request.form['tipo_consulta']
        ag.descricao = request.form['descricao']
        ag.profissional_id = request.form['profissional']
        ag.data = request.form['data']
        ag.hora = request.form['hora']
        if not id:
            db.session.add(ag)
        db.session.commit()

        # Envia confirmação e agenda lembrete
        enviar_email_confirmacao(ag)
        agendar_lembrete(ag)

        flash("Agendamento salvo e e-mail enviado!", "success")
        return redirect(url_for('agendamentos'))

    return render_template(
        'agendamentos.html',
        agendamentos=Agendamento.query.order_by(Agendamento.data).all(),
        clientes=clientes,
        procedimentos=procedimentos,
        profissionais=profissionais,
        agendamento_edit=agendamento_edit
    )

@app.route('/editar_agendamento/<int:id>')
def editar_agendamento(id):
    return agendamentos_render(Agendamento.query.get_or_404(id))

def agendamentos_render(editado):
    return render_template(
        'agendamentos.html',
        agendamentos=Agendamento.query.order_by(Agendamento.data).all(),
        clientes=Cliente.query.all(),
        procedimentos=Procedimento.query.all(),
        profissionais=Profissional.query.all(),
        agendamento_edit=editado
    )

@app.route('/alterar_status_agendamento/<int:agendamento_id>', methods=['POST'])
def alterar_status_agendamento(agendamento_id):
    ag = Agendamento.query.get_or_404(agendamento_id)
    acao = request.form['acao']
    if acao == 'confirmar':
        ag.status = 'Confirmado'
    elif acao == 'concluir':
        ag.status = 'Concluído'
    elif acao == 'cancelar':
        ag.status = 'Cancelado'
    db.session.commit()
    return redirect(url_for('agendamentos'))

# --- RELATÓRIOS
@app.route('/relatorios')
def relatorios():
    return render_template('relatorios.html', agendamentos=Agendamento.query.all())

@app.route('/exportar-pdf', methods=['POST'])
def exportar_pdf():
    html = render_template('pdf_agendamentos.html', agendamentos=Agendamento.query.all())
    resultado = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=resultado)
    if pisa_status.err:
        return "Erro ao gerar PDF", 500

    response = make_response(resultado.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=relatorio_agendamentos.pdf'
    return response

# EXECUTAR APLICAÇÃO
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
