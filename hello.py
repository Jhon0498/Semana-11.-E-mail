from flask import Flask, request, render_template, session, url_for, redirect, flash
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_migrate import Migrate

# Configuração do app
app = Flask(__name__)

# Configurações do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave forte'  # Defina uma chave secreta forte para o WTF Forms

# Inicialização do banco de dados e migrações
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Inicialização do Moment (para manipulação de data/hora)
moment = Moment(app)

# Modelos do banco de dados
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User {self.username}>'

# Função para inicializar os roles
def init_roles():
    # Verificar se os roles já existem, caso contrário, inseri-los
    if Role.query.filter_by(name='Administrator').first() is None:
        admin_role = Role(name='Administrator')
        db.session.add(admin_role)
    if Role.query.filter_by(name='Moderator').first() is None:
        mod_role = Role(name='Moderator')
        db.session.add(mod_role)
    if Role.query.filter_by(name='User').first() is None:
        user_role = Role(name='User')
        db.session.add(user_role)

    db.session.commit()  # Confirma as alterações no banco de dados

# Chamada para inicializar os roles no contexto do app
with app.app_context():
    init_roles()

# Formulário de usuário
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    role = SelectField('Role?:', coerce=int)
    submit = SubmitField('Submit')

# Rota para o formulário e cadastro de usuário
@app.route('/', methods=['GET', 'POST'])
def hello_world():
    form = NameForm()

    # Carregar as opções de role para o SelectField
    form.role.choices = [(role.id, role.name) for role in Role.query.all()]

     # Obter dados do banco de dados
    all_user = User.query.all()
    cont_user =  len(all_user) # para contar usuários
    all_role_user = Role.query.all()
    cont_role = len(all_role_user) #contar role


    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            # Obtém o role escolhido pelo usuário no formulário
            user_role = Role.query.get(form.role.data)
            user = User(username=form.name.data, role_id=user_role.id)
            db.session.add(user)
            db.session.commit()
            flash('Adicionado novo usuário')
        else:
            flash('Já conheço ele')

        session['name'] = form.name.data
        return redirect(url_for('hello_world'))

    return render_template('formulario.html',
    form=form,
    name=session.get('name'),
    pessoa=all_user,
    count_user = cont_user,
    count_role = cont_role,
    all_role_user= all_role_user)


# Rota para exibir detalhes do usuário
@app.route('/user/<name>')
def hello_pront(name):
    return render_template('user.html', name=name, pront='PT3026931', ins='IFSP', current_time=datetime.utcnow())

# Rota para tratamento de erro 404
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404

# Rota para exibir detalhes do contexto da requisição
@app.route('/contextorequisicao')
def hello_requisi_detalhes():
    navegador = request.headers.get('User-Agent')
    ip_remoto = request.headers.get('X-Forwarded-For')
    host_name = request.headers.get('Host')
    return render_template('contextorequisicao.html', name='Jhonatan', navegador=navegador, IP_cliente=ip_remoto, host_name=host_name)

# Contexto do shell para facilitar o uso do banco de dados
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)

if __name__ == '__main__':
    app.run(debug=True)
