from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, PasswordField, SubmitField, SearchField, EmailField, SelectField


class LoginForm(FlaskForm):
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    search = SearchField(validators=[DataRequired()])
    login = SubmitField()


class SignupForm(FlaskForm):
    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    org_name = StringField(name="company_name", validators=[DataRequired()])
    email = EmailField("Email Address", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit', id="nextLogin")
    company_size = SelectField(choices=[('', 'How many employees do you have?'), ('1', '1 - 5 employees'),
                                        ('2', '6 - 10 employees'), ('3', '11 - 20 employees'),
                                        ('4', '21 - 50 employees'), ('4', '51 - 100 employees'),
                                        ('5', '100+ employees')], validators=[DataRequired()])
