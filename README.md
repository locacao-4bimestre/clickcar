# Projeto — Site de Locação de Veículos

## Visão Geral

Este projeto tem como objetivo desenvolver um **site de locação de veículos**, com duas áreas principais:

* **Área pública:** onde os usuários podem pesquisar, visualizar e reservar veículos disponíveis.
* **Área administrativa:** voltada para administradores e funcionários gerenciarem veículos, reservas e usuários.

---

## Funcionalidades Principais

* Busca filtrada por **nome**, **marca** e **ano**;
* **Design responsivo** (funciona em celulares, tablets e computadores);
* **Cadastro e login de usuários**;
* **Controle de acesso** (Admin, Funcionário, Cliente);
* **Autenticação segura** com criptografia de senhas;
* **Painel administrativo** para gerenciar veículos e reservas;
* **Banco de dados relacional** para armazenar todas as informações.

---

## ⚙️ Tecnologias Utilizadas

### Backend

* **Flask (Python)** — servidor web e rotas da API;
* **SQLAlchemy** — ORM para manipulação do banco de dados;
* **Flask-Login / JWT** — autenticação e controle de sessão;
* **SQLite** (desenvolvimento) / **PostgreSQL** (produção);

### Frontend

* **HTML5, CSS3, JavaScript**;
* **Bootstrap / Tailwind CSS** para o design responsivo.

---

## Modelagem de Dados

* **Users:** id, nome, email, senha_hash, role
* **Brands:** id, nome
* **Models:** id, nome, brand_id
* **Vehicles:** id, placa, modelo, ano, cor, preço_diária, status, imagem
* **Rentals:** id, user_id, vehicle_id, data_início, data_fim, total, status

---

## Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seuusuario/locadora-tcc.git
cd locadora-tcc
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar o servidor backend

```bash
flask run
```

O site ficará disponível em: `http://localhost:5000`

---

## Perfis de Acesso

* **Admin:** gerencia veículos, reservas e usuários.
* **Funcionário:** gerencia reservas e veículos.
* **Cliente:** pode buscar veículos, reservar e ver histórico.

---

## Próximos Passos

1. Implementar backend (Flask + SQLAlchemy);
2. Criar banco e models (Users, Vehicles, Rentals);
3. Criar rotas públicas (busca e detalhes do veículo);
4. Implementar sistema de login e cadastro;
5. Desenvolver painel admin;
6. Finalizar o design e tornar o site responsivo.

---

## Equipe do Projeto

**Curso:** Desenvolvimento de Sistemas — IFSP Campus São Paulo
**Disciplina:** Laboratório de Programação, Desenvolvimento Web, Banco de Dados e Artes Visuais Digitais
**Tema:** Sistema Web para Locação de Veículos
**Alunos:** Vitória Xavier e João Paulo Queiroz

---

## 🏁 Licença

Este projeto é de uso acadêmico e foi desenvolvido apenas para fins educacionais.
