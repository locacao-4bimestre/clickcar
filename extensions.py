import os
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from sqlalchemy import create_engine
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
gemini = genai.Client(api_key=os.getenv("api_key"))
db = SQLAlchemy()
mail = Mail()

basedir = os.path.abspath(os.path.dirname(__file__))

database_url = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'locacao.db')

engine = create_engine(database_url, echo=False, future=True)
