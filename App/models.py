from App import db, bcrypt, login_manager
from flask_login import UserMixin
from flask import session
from flask import json


@login_manager.user_loader
def load_user(user_id):
    login_type = session.get('user_type')
    if(login_type == 'directeur'):
        return directeur.query.get(int(user_id))
    if(login_type=="employee"):
        return employee.query.get(int(user_id))
    else:
        return admin.query.get(int(user_id))


class admin(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)

    def __init__(self,username,password):
        self.username = username
        self.password = password

    def get_id(self):
        return self.id
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
        # it will return yes if the attempted password is the same as the encrypted pass


class directeur(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    firstName = db.Column(db.String(length=30), nullable=True)
    lastName = db.Column(db.String(length=30), nullable=True)
    phone = db.Column(db.Integer())
    email_adress = db.Column(db.String(length=50), nullable=False, unique=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    departement = db.Column(db.String(length=200), nullable=True)
    poste = db.Column(db.String(length=200), nullable=True)
    state = db.Column(db.Integer(),default=0)
    Projects = db.relationship('projet', backref='owned_projects',cascade="all,delete" ,lazy=True)

    def get_id(self):
        return self.id

    def get_state(self):
        return self.state
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class employee(db.Model,UserMixin):
    id = db.Column(db.Integer(), primary_key=True,autoincrement=True)
    firstName = db.Column(db.String(length=30), nullable=True)
    lastName = db.Column(db.String(length=30), nullable=True)
    phone = db.Column(db.String(length=20))
    poste = db.Column(db.String(length=200), nullable=False)
    email_adress = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    projet_id = db.Column(db.Integer(), db.ForeignKey('projet.id'))
    Tasks = db.relationship('task', backref='tasks_to_do',cascade="all,delete", lazy=True)

    def get_id(self):
        return self.id
    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class projet(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    projet_title = db.Column(db.String(length=200), nullable=False)
    projet_description = db.Column(db.String(length=1024), nullable=False)
    direct_id = db.Column(db.Integer(), db.ForeignKey('directeur.id'))
    Employees = db.relationship('employee', backref='employees', lazy=True)
    tasks = db.relationship('task', backref='tasks',cascade="all,delete", lazy=True)


class task(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    task_title = db.Column(db.String(length=200), nullable=False)
    task_description = db.Column(db.String(length=1024), nullable=False)
    status = db.Column(db.Integer(),default=0)
    employee_id = db.Column(db.Integer(), db.ForeignKey('employee.id'))
    projet_id = db.Column(db.Integer(), db.ForeignKey('projet.id'))

    def toJson(self):
        return {"id":self.id,
            "title":self.task_title,
            "description":self.task_description,
            "status":self.status
        }
