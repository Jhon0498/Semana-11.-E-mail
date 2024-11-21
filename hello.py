from flask import Flask, request, render_template, session, url_for, redirect, flash
from datetime import datetime

#Parte SQL
import os
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))


from flask_moment import Moment
#Parte do WTF
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)

#parte SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True )
    name = db.Column(db.String(64), unique = True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

#Parte do WTF
app.config['SECRET_KEY'] = 'chave forte'

moment = Moment(app)

#Parte Migrate
from flask_migrate import Migrate
migrate = Migrate(app, db)

class NameForm(FlaskForm):
    name = StringField('Qual teu nome?', validators = [DataRequired()])
    submit = SubmitField('Submit')

#Essa rota está para uso do forms
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = NameForm()
    all_user = User.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user_role = Role.query.filter_by(name='User').first()
            user = User(username=form.name.data, role_id = user_role.id)
            db.session.add(user)
            db.session.commit()
            flash('Adicionado novo usuário')
        else:
            flash('Já conheço ele')
        session['name'] = form.name.data
        return redirect(url_for('hello_world'))
    return render_template('formulario.html', form = form, name = session.get('name'), pessoa = all_user)

"""
@app.route('/')
def hello_world():
    name = "eu estou usando o JINJA2!";
    return render_template('template-base.html', current_time = datetime.utcnow());
"""
@app.route('/user/<name>')
def hello_pront(name):
    name2 = name
    return render_template('user.html', name = name, pront = 'PT3026931', ins = 'IFSP' , current_time = datetime.utcnow())
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', current_time = datetime.utcnow()), 404;
@app.route('/contextorequisicao')
def hello_requisi_detalhes():
    navegador = request.headers.get('User-Agent')
    Ip_remoto = request.headers.get('X-Forwarded-For')
    host_name = request.headers.get('Host')
    return render_template('contextorequisicao.html', name = 'Jhonatan', navegador = navegador, IP_cliente = Ip_remoto, host_name = host_name);

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)