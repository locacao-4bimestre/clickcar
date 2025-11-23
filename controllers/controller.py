import re
from datetime import datetime, timedelta
import os
import string
import random
import secrets
from flask_mail import Message
from sqlalchemy import create_engine, text
from werkzeug.utils import secure_filename
from flask import Blueprint, jsonify, make_response, render_template, request, redirect, url_for, flash, current_app as app
from models.models import db, Usuario, Perfil, Veiculo, TipoVeiculo, Cliente, VehiclePhoto, Token, Reserva
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import sessionmaker, scoped_session
from extensions import mail, basedir, gemini, types
from datetime import date, datetime


database_url = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'locacao.db')
try:
    engine = create_engine(database_url, echo=False, future=True)
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Conexão SQLite bem-sucedida!')
except Exception as e:
    print('Não foi possivel conectar ao sqlite:', e)

main = Blueprint('main', __name__)
SessionLocal = scoped_session(sessionmaker(bind=engine))
# ===================================
# Funções utilitárias
# ===================================


def format_brl(value):
    try:
        # Converte para float
        number = float(value)
    except:
        return "0,00"

    # Formato americano com thousand separator
    formatted = f"{number:,.2f}"  # exemplo -> "1,234,567.89"

    # Quebra em parte inteira e decimal
    inteiro, decimal = formatted.split(".")

    # Troca milhar: "," → "."
    inteiro = inteiro.replace(",", ".")

    # Junta no formato brasileiro
    return f"{inteiro},{decimal}"


def brl(value):
    return format_brl(value)


main.add_app_template_filter(brl, 'brl')


def datebr(value):
    return value.strftime('%d/%m/%Y %H:%M')


main.add_app_template_filter(datebr, 'datebr')


def _only_digits(s: str) -> str:
    return re.sub(r'\D', '', s or '')


# Regex para telefone brasileiro (formato ou só dígitos)
_RE_TELEFONE = re.compile(
    r"""
    ^                         # início
    (?:\(?\d{2}\)?[\s-]?)?    # DDD opcional: (11) ou 11 ou 11- ou 11 espaço
    (?:9\d{4}|\d{4})[-]?\d{4}$ # celular com 9 (9xxxx xxxx) ou fixo (xxxx xxxx)
    """,
    re.VERBOSE
)


def is_valid_telefone(tel: str) -> bool:
    """
    Valida telefone fixo e celular brasileiros.
    Aceita:
    - (11) 91234-5678
    - 11 91234-5678
    - 11912345678
    - (11) 2345-6789
    - 1123456789
    """
    if not tel:
        return False

    digits = re.sub(r"\D", "", tel)

    # Verifica tamanho: fixo (10) ou celular (11)
    if len(digits) not in (10, 11):
        return False

    # Se for celular (11 dígitos), precisa começar com 9
    if len(digits) == 11 and digits[2] != "9":
        return False

    # Se for fixo (10 dígitos), NÃO pode começar com 9
    if len(digits) == 10 and digits[2] == "9":
        return False

    return bool(_RE_TELEFONE.match(tel.strip()))


# -----------------------
# CPF: formato e checksum


def is_valid_cpf(cpf: str) -> bool:
    """
    Valida CPF:
    - aceita formatos com ou sem pontuação: 123.456.789-09 ou 12345678909
    - verifica tamanho, sequências óbvias (todos dígitos iguais) e dígitos verificadores
    """
    if not cpf:
        return False
    cpf = _only_digits(cpf)
    if len(cpf) != 11:
        return False
    # rejeita sequências como 11111111111
    if cpf == cpf[0] * 11:
        return False

    def _calc_digit(digs: str) -> str:
        soma = 0
        peso = len(digs) + 1
        for ch in digs:
            soma += int(ch) * peso
            peso -= 1
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    dv1 = _calc_digit(cpf[:9])
    dv2 = _calc_digit(cpf[:9] + dv1)
    return cpf[-2:] == dv1 + dv2


# -----------------------
# CEP (Correios): 5 dígitos + hífen + 3 dígitos ou 8 dígitos juntos
_RE_CEP = re.compile(r'^\d{5}-?\d{3}$')


def is_valid_cep(cep: str) -> bool:
    """
    Valida CEP no formato 12345-678 ou 12345678
    """
    if not cep:
        return False
    return bool(_RE_CEP.match(cep.strip()))


# -----------------------
# CNH: validar formato (11 dígitos) + rejeita sequências repetidas
# Nota: validação completa exige cálculo de dígitos segundo regra específica da CNH.
_RE_CNH = re.compile(r'^\d{11}$')


def is_valid_cnh(cnh: str) -> bool:
    """
    Validação básica de CNH:
    - aceita somente 11 dígitos
    - rejeita sequências de dígitos idênticos (ex: 11111111111)
    """
    if not cnh:
        return False
    c = _only_digits(cnh)
    if not _RE_CNH.match(c):
        return False
    if c == c[0] * 11:
        return False
    # Observação: validação completa da CNH envolve os dígitos verificadores usados pelo Detran.
    # Se quiser, posso implementar a checagem completa (requer confirmação do algoritmo desejado).
    return True


# -----------------------
# Email: regex prática (não 100% RFC5322, mas cobre a vasta maioria de casos)
_RE_EMAIL = re.compile(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$')


def is_valid_email(email: str) -> bool:
    """
    Valida email com regex prática:
    - parte local: letras, números, . _ % + -
    - domínio: letras/números e hífen, com ao menos um ponto e TLD com 2+ letras
    """
    if not email:
        return False
    return bool(_RE_EMAIL.match(email.strip()))


# -----------------------
# RG: variações por estado — aqui aceitamos 7 a 9 dígitos ou com pontuação (ex.: 12.345.678-9)
_RE_RG = re.compile(r'^\d{7,9}$')
_RE_RG_FORMATADO = re.compile(r'^\d{1,2}\.?\d{3}\.?\d{3}-?\d?$')


def is_valid_rg(rg: str) -> bool:
    """
    Validação básica de RG:
    - aceita 7 a 9 dígitos (após remover não-dígitos)
    - aceita formatos comuns com pontos/hífens
    Observação: RG oficial pode incluir letra (em poucos estados) ou regras regionais.
    """
    if not rg:
        return False
    only = _only_digits(rg)
    if 7 <= len(only) <= 9:
        return True
    # fallback: verificar formato com regex que aceita pontuação
    return bool(_RE_RG_FORMATADO.match(rg.strip()))


# lógica de negócios

def isBeforeToday(date):
    if not date:
        return True
    return date < datetime.now().date()


def isAfterTheTarget(target, date):
    if not date or not target:
        return False
    return date > target


def validate_password(password: str):
    if len(password) < 8:
        return False
    letters = string.ascii_letters
    numbers = string.digits
    special = string.punctuation
    num_letters = 0
    num_nums = 0
    num_specials = 0

    for char in password:
        if char in letters:
            num_letters += 1
        elif char in numbers:
            num_nums += 1
        elif char in special:
            num_specials += 1
        else:
            return False
    if (num_letters > 0) and (num_nums > 0) and (num_specials > 0):
        return True
    return False


def logged_cliente():
    return request.cookies.get("cliente_id")


def allButWhiteSpace():
    allButWhiteSpace = [
        char for char in string.printable if char not in string.whitespace]
    return allButWhiteSpace


def generate_token(size: int):
    allbutwhite = allButWhiteSpace()
    token = ""
    for i in range(0, size):
        randomChar = allbutwhite[random.randint(0, len(allbutwhite)-1)]
        token += randomChar

    return token


def recalc_valor_diaria(data_inicio: date, data_fim: date, veiculo_id):
    db = SessionLocal()
    veiculo = db.query(Veiculo).filter_by(id=veiculo_id).first()
    return calc_valor_total(data_inicio, data_fim, veiculo.preco_por_dia)


def calc_valor_total(data_inicio: date, data_fim: date, diaria):
    periodo = (data_fim - data_inicio).days + 1
    valor_total = periodo * diaria
    return valor_total


def send_email_with_id(usuario_id, subject, html):
    db = SessionLocal()
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    msg = Message(
        subject=subject,
        recipients=[usuario.email],  # para quem vai
        html=html
    )
    mail.send(msg)


def verifyToken(token1, token2):
    print(token1, token2)
    if token1 == token2:
        return True
    return False


def create_token(usuario_id):
    print("Criando")
    db = SessionLocal()
    try:
        token = generate_token(6)
        database_token = Token(
            token=token,
            criado_em=datetime.now(),
            usuario_id=usuario_id
        )
        print("Criando ...")
        send_email_with_id(
            usuario_id, subject="Token - ClickCar", html=f"<p align='center' style='font-size: 15px;'> Seu token de verificação é: </p> <br> <p align='center' style='font-size: 20px;'>{database_token.token} </p> <br> <p style='font-size: 10px;'>* Esse email é automático, por favor não o responda</p>")

        db.add(database_token)
        db.commit()
    except Exception as e:
        print("Não foi possível gerar token", e)


def findLastToken(usuario_id):
    db = SessionLocal()
    token = db.query(Token).filter_by(usuario_id=usuario_id).order_by(
        Token.criado_em.desc()).first()
    return token


def time_to_expire(token: Token):
    print("Criado em: ", token.criado_em, "Hoje: ", datetime.now())
    time = (token.criado_em + timedelta(minutes=3)) - datetime.now()
    print(time.total_seconds() > 0)
    if time.total_seconds() > 0:
        return {
            'min': (time.total_seconds() // 60),
            'sec': (time.total_seconds() % 60),
            'total': (time.total_seconds())
        }
    return {
        'min': 0,
        'sec': 0,
        'total': 0
    }


def isTokenExpired(token: Token):
    token_time = token.criado_em
    if datetime.now() < (token_time + timedelta(minutes=3)):
        return False
    else:
        return True


# ===========================================================
# ÁREA DO CLIENTE
# ===========================================================


@main.route('/customer')
@login_required
def customer_dashboard():
    if current_user.perfil.nome_perfil != 'Cliente':
        flash("Acesso permitido apenas para clientes.", "warning")
        return redirect(url_for('main.index'))
    print(current_user.id, logged_cliente())
    return render_template('customer/dashboard.html', user_id=current_user.id)


@main.route('/customer/profile')
@login_required
def customer_profile():

    if current_user.perfil.nome_perfil != 'Cliente':

        flash("Acesso negado.", "danger")
        return redirect(url_for('main.index'))
    return render_template('customer/profile.html', user=current_user)


@main.route('/customer/profile/edit', methods=['GET', 'POST'])
@login_required
def customer_edit_profile():
    if current_user.perfil.nome_perfil != 'Cliente':
        flash("Acesso negado.", "danger")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']

        cnh = request.form.get("cnh")

        if email != current_user.email:
            user = Usuario.query.filter_by(email=email).first()
            # Verificar email duplicado
            if user:
                if not user.email_verificado:
                    flash("Esse email já está cadastrado. Verifique-o ", "warning")
                    return redirect(url_for('main.verify_user_email', user_id=user.id))
                flash("Esse email já está cadastrado. Logue em sua conta", "warning")
                return redirect(url_for('main.login'))

        perfil_cliente = Perfil.query.filter_by(nome_perfil="Cliente").first()

        email_valido = is_valid_email(email)
        cnh_valida = is_valid_cnh(cnh)
        telefone_valido = is_valid_telefone(telefone)
        if (not cnh_valida or not telefone_valido or not email_valido):
            if not telefone_valido:
                flash("Telefone inválido, use 11 9XXXX-XXXX ou 11 XXXX-XXXX", 'warning')
            if not cnh_valida:
                flash("CNH inválida", 'warning')
            if not email_valido:
                flash(
                    "Email inválido", 'warning')
            return redirect(url_for("main.customer_edit_profile"))

        current_user.nome = request.form['nome']

        current_user.telefone = request.form.get('telefone')
        current_user.endereco = request.form.get('endereco')
        current_user.cnh = request.form.get("cnh")
        print(current_user.email, email, current_user.email != email)
        if email != current_user.email:

            current_user.email_verificado = False
            user = Usuario.query.filter_by(email=email).first()
            # Verificar email duplicado
            if user:
                if not user.email_verificado:
                    flash("Esse email já está cadastrado. Verifique-o ", "warning")
                    return redirect(url_for('main.verify_user_email', user_id=user.id))
                flash("Esse email já está cadastrado. Logue em sua conta", "warning")
                return redirect(url_for('main.login'))
            current_user.email = request.form['email']
            db.session.commit()
            flash("Dados atualizados, verifique seu email!", 'info')
            return redirect(url_for('main.verify_user_email', user_id=current_user.id))
        db.session.commit()
        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for('main.customer_profile'))

    return render_template('customer/profile_edit.html', user=current_user)


@main.route("/minhasreservas/<int:user_id>")
def customer_rentals(user_id):

    usuario_logado_id = logged_cliente()
    print(usuario_logado_id, user_id)
    if (str(user_id) == usuario_logado_id):
        db = SessionLocal()
        reservas = db.query(Reserva).filter_by(user_id=user_id).all()
        print(reservas)
        return render_template("customer/users_rentals.html", reservas=reservas)
    flash("Você não está autorizado a entrar nessa página", "error")
    return redirect(url_for("main.index"))
# ===========================================================
# HOME
# ===========================================================


@main.route('/')
def index():
    veiculos = Veiculo.query.all()
    return render_template('index.html', veiculos=veiculos)


# ===========================================================
# SUBPÁGINAS
# ===========================================================
@main.route('/requirements')
def requisitos():
    return render_template('pages/requirements.html')


@main.route('/faq')
def faq():
    return render_template('pages/faq.html')


# ===========================================================
# LOGIN
# ===========================================================
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        user = Usuario.query.filter_by(email=email).first()

        if user and check_password_hash(user.senha_hash, senha):
            if user.email_verificado:

                login_user(user)
                print(user.perfil)
                if user.perfil.nome_perfil == "Cliente":
                    resp = make_response(
                        redirect(url_for('main.customer_dashboard')))
                    resp.set_cookie('cliente_id', str(user.id), httponly=True)
                    return resp
                else:
                    resp = make_response(redirect(url_for('main.index')))
                    resp.set_cookie('cliente_id', str(user.id), httponly=True)
                    return resp
            else:

                flash("Verifique seu email", "info")
                create_token(user.id)
                return redirect(url_for("main.verify_user_email", user_id=user.id))

        flash('Credenciais incorretas', 'danger')

    return render_template('auth/login.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        cpf = request.form['cpf']  # PEGANDO CPF
        endereco = request.form['endereco']
        senha = request.form['senha']

        user = Usuario.query.filter_by(email=email).first()
        # Verificar email duplicado
        if user:
            if not user.email_verificado:
                flash("Esse email já está cadastrado. Verifique-o ", "warning")
                return redirect(url_for('main.verify_user_email', user_id=user.id))
            flash("Esse email já está cadastrado. Logue em sua conta", "warning")
            return redirect(url_for('main.login'))

        perfil_cliente = Perfil.query.filter_by(nome_perfil="Cliente").first()
        senha_validada = validate_password(senha)
        email_valido = is_valid_email(email)
        cpf_valido = is_valid_cpf(cpf)
        telefone_valido = is_valid_telefone(telefone)
        if (not senha_validada or not email_valido or not cpf_valido or not telefone_valido):
            if not senha_validada:
                flash(
                    "A senha precisa conter ao menos 8 digítos um caractere especial, uma letra normal e um número", "warning")
            if not email_valido:
                flash(
                    "Email inválido", 'warning')
            if not cpf_valido:
                flash("Cpf inválido ", 'warning')
            if not telefone_valido:
                flash("Telefone inválido, use 11 9XXXX-XXXX ou 11 XXXX-XXXX", 'warning')
            return redirect(url_for("main.register"))
        novo = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,   # SALVANDO CPF
            endereco=endereco,
            senha_hash=generate_password_hash(senha),
            perfil_id=perfil_cliente.id,
            email_verificado=False,      # como não tem verificação por email
            codigo_verificacao=None
        )

        db.session.add(novo)
        db.session.commit()
        user_id = novo.id
        create_token(user_id)
        flash("Conta criada com sucesso!", "success")
        print("indo para a verificacao... ")
        return redirect(url_for('main.verify_user_email', user_id=user_id))

    return render_template('auth/register.html')


@main.route("/email-test")
def email_test():
    msg = Message(subject="Test!", recipients=[
                  'joaopauloqueirozcosta@gmail.com'], body="ClickCar")
    mail.send(msg)
    return "OK"


@main.route("/verify/<int:user_id>", methods=["POST", "GET"])
def verify_user_email(user_id):
    method = request.method
    if method == "POST":
        form = request.form
        form_token = form.get("token")
        print("Token recebido: ", form_token)
        last_token = findLastToken(user_id)
        if (verifyToken(form_token, last_token.token)):
            print(isTokenExpired(last_token))
            if (not isTokenExpired(last_token)):
                db = SessionLocal()
                usuario = db.query(Usuario).filter_by(id=user_id).first()
                usuario.email_verificado = True
                db.commit()
                flash("Conta verificada! Faça o login para continuar ", "success")
                return redirect(url_for("main.login"))
            else:
                flash("Token expirado! Enviando outro...", "error")
                create_token(user_id)
                return redirect(url_for("main.verify_user_email", user_id=user_id))
        flash("Token inválido", "error")
        return redirect(url_for("main.verify_user_email", user_id=user_id))
    return render_template('auth/auth_login.html', user_id=user_id)


@main.route("/newToken/<int:user_id>", methods=["POST", "GET"])
def new_token(user_id):
    create_token(user_id)
    flash("Token gerado, confira seu email", "info")
    print("indo para a verificacao... ")
    return redirect(url_for('main.verify_user_email', user_id=user_id))


@main.route('/logout')
@login_required
def logout():
    resp = make_response(redirect(url_for("main.index")))
    resp.delete_cookie("cliente_id")
    logout_user()
    return resp


# =====================
# Usuarios
# ===============

@main.route("/admin/usuario")
def admin_usuario_page():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    return render_template("admin/users/list.html", usuarios=usuarios)


@main.route("/admin/usuario/edit/<int:user_id>", methods=["POST", "GET"])
def edit_user(user_id):
    db = SessionLocal()
    usuario = db.query(Usuario).filter_by(id=user_id).first()
    if not usuario:
        flash("Este usuário não existe", "error")
        return redirect(url_for("main.admin_usuario_page"))
    perfis = db.query(Perfil).all()
    method = request.method
    if method == "POST":

        form = request.form
        nome = form.get("nome")
        email = form.get("email")
        perfil = form.get("perfil")
        telefone = form.get("telefone")
        cpf = form.get("cpf")
        endereco = form.get("endereco")
        if db.query(Usuario).filter_by(email=email).first():
            flash("Outro usuário possui este email ", "error")
            return redirect(url_for("main.edit_user", user_id=user_id))
        usuario.nome = nome
        usuario.email = email
        usuario.perfil_id = perfil
        usuario.telefone = telefone
        usuario.cpf = cpf
        usuario.endereco = endereco
        db.commit()
        flash("Usuário alterado! ", "success")
        return redirect(url_for("main.edit_user", user_id=user_id))
    return render_template("admin/users/edit.html", usuario=usuario, perfis=perfis)


@main.route("/excluir_usuario/<int:user_id>")
def admin_excluir_usuario(user_id):
    db = SessionLocal()
    usuario = db.query(Usuario).filter_by(id=user_id).first()
    if not usuario:
        flash("Esse usuário não existe", "error")
        return redirect(url_for("main.admin_usuario_page"))
    else:
        db.delete(usuario)
        db.commit()
        flash(f"Usuario {usuario.nome} deletado ", "success")
        return redirect(url_for("main.admin_usuario_page"))


# Reservas

@main.route("/admin/reservas")
def listar_reservas():
    db = SessionLocal()
    reservas = db.query(Reserva).all()
    return render_template("admin/rentals/list.html", reservas=reservas)


@main.route("/admin/reservas/edit/<int:id>", methods=["POST", "GET"])
def edit_reserva(id):
    db = SessionLocal()
    statuses = ["pendente", "confirmada", "cancelada"]
    reserva = db.query(Reserva).filter_by(id=id).first()
    if not reserva:
        flash("Esta reserva não existe ", "error")
        return redirect(url_for("main.listar_reservas"))
    if request.method == "POST":
        form = request.form
        user_id = form.get("user")
        veiculo_id = form.get("veiculo")
        data_inicio = date.fromisoformat(form.get("data_inicio"))
        data_fim = date.fromisoformat(form.get("data_fim"))
        status = form.get("status")
        print(status)
        reserva.user_id = user_id
        reserva.veiculo_id = veiculo_id
        reserva.data_inicio = (data_inicio)
        reserva.data_fim = (data_fim)
        reserva.status = status
        reserva.valor_total = recalc_valor_diaria(
            data_inicio, data_fim, veiculo_id)
        db.commit()
        flash("Reserva editada! ", 'success')
        return redirect(url_for("main.edit_reserva", id=id))
    return render_template("admin/rentals/edit.html", reserva=reserva, statuses=statuses)


@main.route("/admin/reservas/excluir/<int:reserva_id>")
def excluir_reserva(reserva_id):
    db = SessionLocal()
    reserva = db.query(Reserva).filter_by(id=reserva_id).first()
    if not reserva:
        flash("Essa reserva não existe", "error")
        return redirect(url_for("main.listar_reservas"))
    else:
        db.delete(reserva)
        db.commit()
        flash("Reserva excluída", "success")
        return redirect(url_for("main.listar_reservas"))

# ===========================================================
# LISTAR VEÍCULOS
# ===========================================================


@main.route('/veiculos')
def listar_veiculos():
    q = request.args.get('q', type=str)
    marca = request.args.get('marca', type=str)
    ano = request.args.get('ano', type=int)

    query = Veiculo.query.filter(Veiculo.status == 'disponivel')

    if q:
        like = f"%{q}%"
        query = query.filter(
            (Veiculo.modelo.ilike(like)) |
            (Veiculo.marca.ilike(like))
        )

    if marca:
        query = query.filter(Veiculo.marca.ilike(f"%{marca}%"))

    if ano:
        query = query.filter(Veiculo.ano == ano)

    veiculos = query.all()
    return render_template('vehicles/list.html', veiculos=veiculos)


# ===========================================================
# ADMIN — CADASTRAR TIPO
# ===========================================================

@main.route("/admin/tipos")
@login_required
def admin_listar_tipos():
    query = TipoVeiculo.query.all()
    return render_template('admin/types/list.html', tipos=query)


@main.route("/admin/tipos/delete/<int:id>")
def delete_tipo(id):
    print("******* delete")
    if current_user.perfil.nome_perfil != 'Admin':
        flash("Apenas administradores podem excluir tipos de veiculos.", "warning")
        return redirect(url_for('main.admin_listar_tipos'))
    try:
        tipo = TipoVeiculo.query.get_or_404(id)
        db.session.delete(tipo)
        db.session.commit()
        flash("Cliente removido!", "success")
        return redirect(url_for('main.admin_listar_tipos'))
    except Exception as E:
        flash("Algum carro utiliza esse tipo, remova antes de remover a categoria", "error")
        return redirect(url_for("main.admin_listar_tipos"))


@main.route('/admin/tipos/novo', methods=['GET', 'POST'])
@login_required
def novo_tipo():
    if current_user.perfil.nome_perfil != 'Admin':
        flash('Acesso negado', 'warning')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']

        tipo = TipoVeiculo(nome=nome, descricao=descricao)
        db.session.add(tipo)
        db.session.commit()

        flash("Tipo cadastrado!", "success")
        return redirect(url_for('main.novo_tipo'))

    return render_template('admin/types/new_type.html')


@main.route('/admin/tipos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_editar_tipo(id):
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    tipo = TipoVeiculo.query.filter_by(id=id).first()
    print(tipo)
    if request.method == 'POST':
        nome = request.form.get("nome")
        desc = request.form.get("dec")
        try:
            tipo.nome = nome
            tipo.desc = desc
            db.session.commit()
            flash("Veículo atualizado!", "success")
            return redirect(url_for('main.admin_listar_tipos'))
        except:
            return redirect(url_for('main.admin_editar_tipo', id=id))
    return render_template("admin/types/edit.html", tipo=tipo)


# ===========================================================
# ADMIN — LISTAR VEÍCULOS
# ===========================================================
@main.route('/admin/vehicles')
@login_required
def admin_listar_veiculos():
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    veiculos = Veiculo.query.all()
    return render_template('admin/vehicles/list.html', veiculos=veiculos)

# ===========================================================
# VER VEÍCULO INDIVIDUAL
# ===========================================================


@main.route('/veiculos/<int:id>', methods=["POST", "GET"])
def ver_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
    if request.method == "POST":
        print("POST")
        db = SessionLocal()
        form = request.form
        if veiculo.status != "disponivel":
            flash("Desculpe, esse veículo não está disponível")
            return redirect(url_for("main.ver_veiculo", id=veiculo.id))
        data_inicio = date.fromisoformat(form.get("data_inicio"))
        data_fim = date.fromisoformat(form.get("data_fim"))
        if (isBeforeToday(data_inicio) or not isAfterTheTarget(data_inicio, data_fim)):
            if not isAfterTheTarget(data_inicio, data_fim):
                flash(
                    "Você não pode reservar um carro com uma data de início maior do que a de entrega!", 'info')
            if isBeforeToday(data_inicio):
                flash(
                    "Você não pode realizar uma reserva para um dia anterior ao dia de hoje", 'info')
            return redirect(url_for("main.ver_veiculo", id=id))
        if not current_user.is_authenticated:
            flash("Faça login para reservar um carro! ", 'info')
            return redirect(url_for("main.ver_veiculo", id=id))
        nova_reserva = Reserva(
            user_id=current_user.id,
            veiculo_id=veiculo.id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status="pendente",
            valor_total=calc_valor_total(
                data_inicio, data_fim, veiculo.preco_por_dia),
            criado_em=datetime.now()
        )
        db.add(nova_reserva)
        db.commit()
        flash("Reserva está pendente! Confira em minhas reservas", "success")
        return redirect(url_for("main.index"))
    return render_template('vehicles/view.html', veiculo=veiculo)


# ===========================================================
# ADMIN — NOVO VEÍCULO
# ===========================================================
@main.route('/admin/vehicles/new', methods=['GET', 'POST'])
@login_required
def admin_novo_veiculo():
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    tipos = TipoVeiculo.query.all()

    if request.method == 'POST':
        novo = Veiculo(
            modelo=request.form['modelo'],
            marca=request.form['marca'],
            ano=request.form['ano'],
            placa=request.form['placa'],
            cor=request.form['cor'],
            tipo_id=request.form['tipo_id'],
            preco_por_dia=request.form['preco_por_dia'],
            status=request.form['status'],
            localizacao=request.form['localizacao']
        )
        db.session.add(novo)
        db.session.commit()

        fotos = request.files.getlist('fotos')
        for f in fotos:
            if f and f.filename:
                filename = secure_filename(f.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                f.save(caminho)

                nova = VehiclePhoto(
                    veiculo_id=novo.id,
                    filename=filename
                )
                db.session.add(nova)

        db.session.commit()
        flash("Veículo cadastrado!", "success")
        return redirect(url_for('main.admin_listar_veiculos'))

    return render_template('admin/vehicles/new.html', tipos=tipos)


# ===========================================================
# ADMIN — EDITAR VEÍCULO
# ===========================================================
@main.route('/admin/vehicles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_editar_veiculo(id):
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    veiculo = Veiculo.query.get_or_404(id)
    tipos = TipoVeiculo.query.all()

    if request.method == 'POST':
        veiculo.modelo = request.form['modelo']
        veiculo.marca = request.form['marca']
        veiculo.ano = request.form['ano']
        veiculo.placa = request.form['placa']
        veiculo.cor = request.form['cor']
        veiculo.tipo_id = request.form['tipo_id']
        veiculo.preco_por_dia = request.form['preco_por_dia']
        veiculo.status = request.form['status']
        veiculo.localizacao = request.form['localizacao']

        novas_fotos = request.files.getlist('fotos')
        for foto in novas_fotos:
            if foto and foto.filename.strip():
                filename = secure_filename(foto.filename)
                caminho = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                foto.save(caminho)

                nova_foto = VehiclePhoto(
                    veiculo_id=veiculo.id,
                    filename=filename
                )
                db.session.add(nova_foto)

        db.session.commit()
        flash("Veículo atualizado!", "success")
        return redirect(url_for('main.admin_listar_veiculos'))

    return render_template('admin/vehicles/edit.html', veiculo=veiculo, tipos=tipos)


# ===========================================================
# ADMIN — EXCLUIR VEÍCULO
# ===========================================================
@main.route('/admin/vehicles/delete/<int:id>')
@login_required
def admin_excluir_veiculo(id):
    if current_user.perfil.nome_perfil != 'Admin':
        flash("Apenas administradores podem excluir veículos.", "warning")
        return redirect(url_for('main.admin_listar_veiculos'))

    veiculo = Veiculo.query.get_or_404(id)
    db.session.delete(veiculo)
    db.session.commit()

    flash("Veículo removido!", "success")
    return redirect(url_for('main.admin_listar_veiculos'))


# ===========================================================
# ADMIN — EXCLUIR FOTO
# ===========================================================
@main.route('/admin/vehicles/photo/delete/<int:foto_id>/<int:veiculo_id>')
@login_required
def admin_excluir_foto(foto_id, veiculo_id):
    foto = VehiclePhoto.query.get_or_404(foto_id)

    caminho = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
    if os.path.exists(caminho):
        os.remove(caminho)

    db.session.delete(foto)
    db.session.commit()

    flash("Foto removida!", "success")
    return redirect(url_for('main.admin_editar_veiculo', id=veiculo_id))


# ===========================================================
# ADMIN — LISTAR CLIENTES
# ===========================================================
@main.route('/admin/customers')
@login_required
def admin_listar_clientes():
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    customers = Cliente.query.all()
    return render_template('admin/customers/list.html', customers=customers)


# ===========================================================
# ADMIN — NOVO CLIENTE
# ===========================================================
@main.route('/admin/customers/new', methods=['GET', 'POST'])
@login_required
def admin_novo_cliente():
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        novo = Cliente(
            nome=request.form['nome'],
            email=request.form['email'],
            telefone=request.form['telefone'],
            cpf=request.form['cpf'],
            endereco=request.form['endereco']
        )
        db.session.add(novo)
        db.session.commit()

        flash("Cliente cadastrado!", "success")
        return redirect(url_for('main.admin_listar_clientes'))

    return render_template('admin/customers/new.html')


# ===========================================================
# ADMIN — EDITAR CLIENTE
# ===========================================================
@main.route('/admin/customers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_editar_cliente(id):
    if current_user.perfil.nome_perfil not in ['Admin', 'Atendimento']:
        flash("Acesso negado", "danger")
        return redirect(url_for('main.index'))

    customer = Cliente.query.get_or_404(id)

    if request.method == 'POST':
        customer.nome = request.form['nome']
        customer.email = request.form['email']
        customer.telefone = request.form['telefone']
        customer.cpf = request.form['cpf']
        customer.endereco = request.form['endereco']

        db.session.commit()
        flash("Cliente atualizado!", "success")
        return redirect(url_for('main.admin_listar_clientes'))

    return render_template('admin/customers/edit.html', customer=customer)


# ===========================================================
# ADMIN — EXCLUIR CLIENTe
# ===========================================================
@main.route('/admin/customers/delete/<int:id>')
@login_required
def admin_excluir_cliente(id):
    if current_user.perfil.nome_perfil != 'Admin':
        flash("Apenas administradores podem excluir clientes.", "warning")
        return redirect(url_for('main.admin_listar_clientes'))

    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()

    flash("Cliente removido!", "success")
    return redirect(url_for('main.admin_listar_clientes'))


@main.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form.get('email')

    if not email:
        flash("Digite um e-mail válido.", "warning")
        return redirect(url_for('main.index'))

    from models.models import Newsletter

    if Newsletter.query.filter_by(email=email).first():
        flash("Este e-mail já está cadastrado!", "info")
        return redirect(url_for('main.index'))

    novo = Newsletter(email=email)
    db.session.add(novo)
    db.session.commit()

    flash("E-mail cadastrado com sucesso! ", "success")
    return redirect(url_for('main.index'))


# API

@main.route("/api/token_time/<int:user_id>")
def token_time(user_id):
    last_token = findLastToken(user_id)
    resp = time_to_expire(last_token)

    return jsonify({
        'min': str(int(resp['min'])),
        'sec': str(int(resp['sec']))
    })


# simulação:
@main.route("/api/simulação", methods=["POST", "GET"])
def get_simulacao():
    db = SessionLocal()
    data = request.get_json()
    inicio = date.fromisoformat(data['inicio'])
    fim = date.fromisoformat(data['fim'])
    veiculo = db.query(Veiculo).filter_by(id=data['veiculo_id']).first()
    if not veiculo or not fim or not inicio:
        return jsonify({
            'status': '404',
            'msg': 'Algo aconteceu, provavelmente um campo faltando'
        })
    if isBeforeToday(inicio) or isBeforeToday(fim):
        return jsonify({
            'status': '404',
            'msg': 'Você não pode reservar um carro para um dia anterior ao dia de hoje!'
        })
    if not isAfterTheTarget(inicio, fim):
        return jsonify({
            'status': '404',
            'msg': 'Você não pode reservar um carro com uma data de início maior do que a de entrega!'
        })
    else:
        return jsonify({
            'status': '200',
            'valor': recalc_valor_diaria(inicio, fim, veiculo.id)
        })


@main.route("/api/chatbot", methods=['POST', 'GET'])
def bot_msg():
    data = request.get_json()
    print(data)
    email_verificado = False
    if current_user.is_authenticated:
        if current_user.email_verificado:
            email_verificado = True
    print(current_user.is_authenticated)
    response = gemini.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=f"""Você está em um site de locadora ajudando um cliente, no geral ajude ele a explorar o site, indicando ele ir para aba de carros, minhas reservas, fazer login caso nao tenha feito, verificar o email se precisar etc." \
            ou caso seja uma duvida diferente tente falar com ele, siga as regras: Não pule linhas entre paragrafos, mande uma mensagem curta e sem 
            textos diferentes como negrito e itálico, contexto: Usuario está logado? : {'sim' if current_user.is_authenticated else 'nao'}, {(f"Ele possui email_verificado: {'sim' if email_verificado else 'não'}") if current_user.is_authenticated else ""}"""),
        contents=data["text"]
    )
    print(response.text)
    return jsonify({
        'ai': 'gemini',
        'model': '2.5',
        'text': response.text
    })
