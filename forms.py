from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo
from programs import PROGRAMS


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Login')


class SignUpForm(FlaskForm):
    firstname = StringField('First Name', validators=[InputRequired(), Length(max=30)])
    lastname = StringField('Last Name', validators=[InputRequired(), Length(max=30)])
    program = SelectField('Program', validators=[InputRequired()], choices=[(program, program) for program in PROGRAMS])
    username = StringField('Username', validators=[InputRequired(), Length(min=5, max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    confirmPassword = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class SearchForm(FlaskForm):
    keyword = StringField('Keywords')
    program = SelectField('Program', choices=[(program, program) for program in PROGRAMS])
    fromDate = DateField('From Date')
    toDate = DateField('To Date')
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(min=2, max=50)])
    message = TextAreaField('Message', validators=[InputRequired()], default="")
    post = SubmitField('Post')
    delete = SubmitField('Delete')



    

