from flask import render_template
from flask_mail import Message
from extensions import mail

# =============================
# E-MAILS PARA CLIENTES
# =============================

def enviar_confirmacao_cadastro(usuario):
    if not usuario or not getattr(usuario, "email", None):
        return
    msg = Message(
        subject="Bem-vinda(o) à Aura Estética!",
        recipients=[usuario.email]
    )
    msg.html = render_template(
        "emails/email_confirmacao_cadastro.html",
        nome=getattr(usuario, "nome", "Cliente")
    )
    mail.send(msg)


def enviar_confirmacao_agendamento(agendamento, cliente, procedimento):
    if not cliente or not getattr(cliente, "email", None):
        return
    msg = Message(
        subject="Agendamento confirmado - Aura Estética",
        recipients=[cliente.email]
    )
    msg.html = render_template(
        "emails/email_confirmacao_agendamento.html",
        nome=getattr(cliente, "nome", "Cliente"),
        data=agendamento.data,
        hora=agendamento.hora,
        profissional=agendamento.profissional,
        procedimento=procedimento.nome if procedimento else "Procedimento"
    )
    mail.send(msg)


def enviar_alteracao_agendamento(agendamento, cliente, procedimento):
    if not cliente or not getattr(cliente, "email", None):
        return
    msg = Message(
        subject="Agendamento alterado - Aura Estética",
        recipients=[cliente.email]
    )
    msg.html = render_template(
        "emails/email_alteracao_agendamento.html",
        nome=getattr(cliente, "nome", "Cliente"),
        data=agendamento.data,
        hora=agendamento.hora,
        profissional=agendamento.profissional,
        procedimento=procedimento.nome if procedimento else "Procedimento"
    )
    mail.send(msg)


def enviar_lembrete_agendamento(agendamento, cliente, procedimento):
    if not cliente or not getattr(cliente, "email", None):
        return
    msg = Message(
        subject="Lembrete de agendamento - Aura Estética",
        recipients=[cliente.email]
    )
    msg.html = render_template(
        "emails/email_lembrete_agendamento.html",
        nome=getattr(cliente, "nome", "Cliente"),
        data=agendamento.data,
        hora=agendamento.hora,
        profissional=agendamento.profissional,
        procedimento=procedimento.nome if procedimento else "Procedimento"
    )
    mail.send(msg)


# =============================
# E-MAILS PARA EMPRESA (EQUIPE AURA ESTÉTICA)
# =============================

EMAIL_EMPRESA = "aura.estetica@empresa.com"  # troque para o e-mail oficial da clínica

def notificar_novo_cadastro(usuario):
    if not usuario:
        return
    msg = Message(
        subject="Novo cadastro de cliente - Aura Estética",
        recipients=[EMAIL_EMPRESA]
    )
    msg.html = render_template(
        "emails/email_novo_cadastro.html",
        nome=getattr(usuario, "nome", "Cliente"),
        email=getattr(usuario, "email", "-")
    )
    mail.send(msg)


def notificar_novo_agendamento(agendamento, cliente, procedimento):
    if not agendamento or not cliente:
        return
    msg = Message(
        subject="Novo agendamento/reagendamento - Aura Estética",
        recipients=[EMAIL_EMPRESA]
    )
    msg.html = render_template(
        "emails/email_novo_agendamento.html",
        nome=cliente.nome,
        data=agendamento.data,
        hora=agendamento.hora,
        profissional=agendamento.profissional,
        procedimento=procedimento.nome if procedimento else "Procedimento"
    )
    mail.send(msg)


def notificar_cancelamento_agendamento(agendamento, cliente, procedimento):
    if not agendamento or not cliente:
        return
    msg = Message(
        subject="Cancelamento de agendamento - Aura Estética",
        recipients=[EMAIL_EMPRESA]
    )
    msg.html = render_template(
        "emails/email_cancelamento_agendamento.html",
        nome=cliente.nome,
        data=agendamento.data,
        hora=agendamento.hora,
        profissional=agendamento.profissional,
        procedimento=procedimento.nome if procedimento else "Procedimento"
    )
    mail.send(msg)

