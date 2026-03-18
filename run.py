import os
import sys

# Agregar el directorio actual al path para que encuentre los módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Importar directamente los módulos sueltos
import models
import routes
import auth as auth_module

app = Flask(__name__, 
    template_folder='.',   # templates están en la raíz
    static_folder='static'
)

app.run(debug=True)