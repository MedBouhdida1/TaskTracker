from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TelField,TextAreaField,EmailField,validators
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from App.models import directeur,employee
import phonenumbers

class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = directeur.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("Username already exists! Please try a different username")

    def validate_email_adress(self, email_adress_to_check):
        email_adress = directeur.query.filter_by(email_adress=email_adress_to_check.data).first()
        if email_adress:
            raise ValidationError("email_adress already exists! Please try a different email_adress")
    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    nom = StringField(label='Name:', validators=[Length(min=2, max=30), DataRequired()])
    lastName = StringField(label='lastName:', validators=[Length(min=2, max=30), DataRequired()])
    phone = TelField(label='Phone', validators=[DataRequired()])
    departement = StringField(label='Departement:', validators=[DataRequired()])
    poste = StringField(label='poste:', validators=[DataRequired()])
    email_adress = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField(label='Create Account')

class loginForm(FlaskForm):
    username = StringField(label='User Name', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')


class loginFormEmp(FlaskForm):
    email_adress = EmailField(label='Email', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Sign In')

class AddProjectForm(FlaskForm):
    project_title=StringField(label='Project Title',validators=[DataRequired()])
    project_description=TextAreaField(label='Project Description',validators=[DataRequired()])
    submit = SubmitField(label='Add project')


class EmployeeForm(FlaskForm):
    def validate_email_adress(self, email_adress_to_check):
        email_adress = employee.query.filter_by(email_adress=email_adress_to_check.data).first()
        if email_adress:
            raise ValidationError("email_adress already exists! Please try a different email_adress")

    def validate_phone(self, phone):
        try:
            p = phonenumbers.parse(phone.data)
            if not phonenumbers.is_valid_number(p):
                raise ValueError()
        except (phonenumbers.phonenumberutil.NumberParseException, ValueError):
            raise ValidationError('Invalid phone number')
    firstName = StringField(label='First Name',validators=[DataRequired()]) #I'll add some messages
    lastName = StringField(label='Last Name',validators=[DataRequired()])
    phone = TelField(label='Phone', validators=[DataRequired()])
    poste = StringField(label='Poste',validators=[DataRequired()])
    email_adress = EmailField(label='Email',validators=[DataRequired(),Email()])
    submit = SubmitField(label='ADD')

class TaskForm(FlaskForm):
    taskTitle = StringField(label='Task Title',validators=[DataRequired()])
    description = TextAreaField(label='description',validators=[DataRequired()])
    submit = SubmitField(label='ADD')

    
