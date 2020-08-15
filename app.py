from datetime import datetime, timedelta
from flask import Flask, render_template, flash, redirect, url_for, session, request, abort
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, SignUpForm, SearchForm, ReviewForm
from flask_bcrypt import Bcrypt
import os
import dotenv

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DEV_DB_URI')
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    program = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now)
    reviews = db.relationship('Reviews', backref='author', lazy=True)

    def __repr__(self):
        return f'Student({self.student_id}, {self.program}, {self.first_name}, {self.last_name}, {self.username}, {self.password}, {self.created_date}, {self.image})'

class Reviews(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student'), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'Reviews({self.review_id}, {self.student_id}, {self.title}, {self.message}, {self.created_date})'


@app.route('/', methods=['GET', 'POST'])
def home():
    searchForm = SearchForm()
    perPage = 10
    page = request.args.get('page', 1, type=int)
    reviews = Reviews.query.order_by(Reviews.created_date.desc()).paginate(page=page, per_page=perPage)
    fromDate = datetime(2020, 8, 1).strftime('%Y-%m-%d')
    toDate = datetime.now().strftime('%Y-%m-%d')
    if request.method == 'POST':
        keyword = searchForm.keyword.data
        program = searchForm.program.data
        fromDate = searchForm.fromDate.data
        toDate = searchForm.toDate.data
        if not fromDate:
            fromDate = datetime(2020, 8, 1)
        if not toDate:
            toDate = datetime.now()

        fromDate = fromDate.strftime('%Y-%m-%d')

        if program and keyword:
            reviews = Reviews.query.join(Student).filter((Student.program==program) & ((Reviews.title.ilike(keyword+'%')) | (Reviews.message.ilike(keyword+'%'))) & (Reviews.created_date >= fromDate) & (Reviews.created_date <= ((toDate + timedelta(days=1)).strftime('%Y-%m-%d')))).order_by(Reviews.created_date.desc()).paginate(page=page, per_page=perPage)
        elif program:
            reviews = Reviews.query.join(Student).filter((Student.program==program) & (Reviews.created_date >= fromDate) & (Reviews.created_date <= ((toDate + timedelta(days=1)).strftime('%Y-%m-%d')))).order_by(Reviews.created_date.desc()).paginate(page=page, per_page=perPage)
        elif keyword:
            reviews = Reviews.query.join(Student).filter((Reviews.title.ilike(keyword+'%')) | (Reviews.message.ilike(keyword+'%')) & (Reviews.created_date >= fromDate) & (Reviews.created_date <= ((toDate + timedelta(days=1)).strftime('%Y-%m-%d')))).order_by(Reviews.created_date.desc()).paginate(page=page, per_page=perPage)

    firstname = None
    lastname = None
    if 'student_id' in session:
        id = session['student_id']
        firstname = Student.query.filter_by(student_id=id).first().first_name
        lastname = Student.query.filter_by(student_id=id).first().last_name
    return render_template('home.html', form=searchForm, reviews=reviews, firstname=firstname, lastname=lastname, toDate=toDate, fromDate=fromDate)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()
        if student and bcrypt.check_password_hash(student.password ,form.password.data):
            flash(f'Welcome {form.username.data}!', 'success')   
            session['student_id'] = student.student_id
            return redirect(url_for('home'),)
        else:
            flash(f'Incorrect username or password!', 'danger')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        newStudent = Student(first_name=form.firstname.data, last_name=form.lastname.data, program=form.program.data, username=form.username.data, password=hashedPassword)
        try:
            db.session.add(newStudent)
            db.session.commit()
            flash(f'Welcome {form.firstname.data} {form.lastname.data} we have created your account!', 'success')
            session['student_id'] = newStudent.student_id
            return redirect(url_for('home'))
        except:
            flash(f'Username {form.username.data} already exists!', 'danger')
    
    return render_template('signup.html', form=form)

@app.route('/logout')
def logout():
    session.pop('student_id', None)
    return redirect(url_for('home'))

@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'student_id' in session:
        form = ReviewForm()
        del form.delete
        id = session['student_id']
        if form.validate_on_submit():
            if form.post.data:
                review = Reviews(student_id=id, title=form.title.data, message=form.message.data)
                db.session.add(review)
                db.session.commit()
                flash('Thanks for you review!', 'success')
                return redirect(url_for('home'))
        else:
            return render_template('review.html', form=form, program=Student.query.get(id).program)
    
    flash('You must be logged first!', 'danger')
    return redirect(url_for('home'))

    
@app.route('/review/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    if 'student_id' in session:
        id = session['student_id']
        review = Reviews.query.get(review_id)
        if review.author.username != Student.query.filter_by(student_id=id).first().username:
            abort(403)
        form = ReviewForm()
        if form.validate_on_submit():
            if form.post.data:
                review.title = form.title.data
                review.message = form.message.data
                db.session.commit()
                flash('Review updated!', 'success')
                return redirect(url_for('home'))
            elif form.delete.data:
                db.session.delete(review)
                db.session.commit()
                flash('Review deleted!', 'danger')
                return redirect(url_for('home'))
        else:
            form.message.data = review.message
            form.title.data = review.title
            return render_template('review.html', form=form, program=review.author.program)

    flash('You must be logged first!', 'danger')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()