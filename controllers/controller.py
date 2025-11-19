from datetime import datetime, timedelta
import os
import secrets
from flask_mail import Message
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app as app
from models.models import db, Usuario, Perfil, Veiculo, TipoVeiculo, Cliente, VehiclePhoto, Token
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.orm import sessionmaker, scoped_session
from app import engine


main = Blueprint('main', __name__)
SessionLocal = scoped_session(sessionmaker(bind=engine))
# ===================================
# Funções utilitárias
# ===================================


def send_email_with_id(usuario_id, subject, body):
    db = SessionLocal()
    usuario = db.query(Usuario).filter_by(id=usuario_id).first()
    msg = Message(
        subject=subject,
        recipients=[usuario.email],  # para quem vai
        body=body
    )
    main.send(msg)


def verifyToken(token1, token2):
    print(token1, token2)
    if token1 == token2:
        return True
    return False


def create_token(usuario_id):
    print("Criando")
    db = SessionLocal()
    try:
        token = secrets.token_urlsafe(32)
        database_token = Token(
            token=token,
            criado_em=datetime.now(),
            usuario_id=usuario_id
        )
        print("Criando ...")
        send_email_with_id(
            usuario_id, subject="Token - ClickCar", body=database_token.token)
        db.add(database_token)
        db.commit()
    except:
        print("Não foi possível gerar token")


def findLastToken(usuario_id):
    db = SessionLocal()
    token = db.query(Token).filter_by(usuario_id=usuario_id).order_by(
        Token.data_criacao.desc()).first()
    return token


def isTokenExpired(token: Token):
    token_time = token.data_criacao
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
    return render_template('customer/dashboard.html')


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
        current_user.nome = request.form['nome']
        current_user.email = request.form['email']
        current_user.telefone = request.form.get('telefone')
        current_user.endereco = request.form.get('endereco')

        db.session.commit()
        flash("Dados atualizados com sucesso!", "success")
        return redirect(url_for('main.customer_profile'))

    return render_template('customer/profile_edit.html', user=current_user)


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
            login_user(user)

            if user.perfil.nome_perfil == "Cliente":
                return redirect(url_for('main.customer_dashboard'))
            else:
                return redirect(url_for('main.index'))

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

        # Verificar email duplicado
        if Usuario.query.filter_by(email=email).first():
            flash("Esse email já está cadastrado.", "warning")
            return redirect(url_for('main.register'))

        perfil_cliente = Perfil.query.filter_by(nome_perfil="Cliente").first()

        novo = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf,   # SALVANDO CPF
            endereco=endereco,
            senha_hash=generate_password_hash(senha),
            perfil_id=perfil_cliente.id,
            email_verificado=True,      # como não tem verificação por email
            codigo_verificacao=None
        )

        db.session.add(novo)
        db.session.commit()

        flash("Conta criada com sucesso!", "success")
        return redirect(url_for('main.login'))

    return render_template('auth/register.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


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


@main.route('/veiculos/<int:id>')
def ver_veiculo(id):
    veiculo = Veiculo.query.get_or_404(id)
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
