from flask import Flask,session
from flask_bcrypt import Bcrypt
import os
# SQLAlchemy (source code) is a well-regarded database toolkit and object-relational mapper (ORM) implementation written in Python.
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mohamedbouhdida100*@localhost/todoapp'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
  # database name

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "login_direc"

from App import routes
from App.models import admin
import App.api


 

