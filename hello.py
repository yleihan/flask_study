from flask import Flask,redirect,session,url_for,flash
from flask_bootstrap import Bootstrap
from flask import render_template
from flask_moment import Moment
from datetime import datetime
from flask_wtf import Form
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
import os
from flask_script import Shell
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from flask_mail import Mail
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY']='sadsaga4g5a67g4da4g4s4ds3a4dsa4g4aada6123a1s3d12s'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=True
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['FALSKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER']='FLASKY Admin yleihan@163.com'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app,db)
mail = Mail(app)



def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX']+subject,sender=app.config['FLASKY_MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.text',**kwargs)
    msg.html = render_template(template + '.html',**kwargs)
    mail.send(msg)



class Role(db.Model):
    __tablename__= 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')
    def __repr__(self):
        return '<Role %r>' % self.name

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),unique=True,index=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))
    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

def make_shell_context():
    return dict (app=app,db=db,User=User,Role=Role)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)


@app.route('/' , methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by (username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known']= False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'],'New User','mail/new_user',user=user)
        else:
            session['known']=True

        session['name'] = form.name.data
        form.name.data = ''

        return redirect(url_for('index'))

    return render_template('index.html',form=form ,name=session.get('name'),known=session.get('known',False))


#@app.route('/<name>')
#def index(name):
#    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_found(e):
    return render_template('500.html'),500




from flask import request
@app.route('/ua')
def ua():
    res = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % res

@app.route('/bad')
def bad():
    return  '<h1>Bad Request</h1>', 400

from flask import make_response
@app.route('/rep')
def rep():
    res = make_response('<h1>>This document carries a cookie!</h1>')
    res.set_cookie('answer','42')
    return res

from flask import redirect
@app.route('/red')
def red():
    return redirect('https://www.baidu.com')

from flask import abort
@app.route('/user/<id>')
def get_user(id):
    user = load_user(id)
    if not user:
        abort(404)
    return  '<h1>Hello, %s</h1>' % user.name





if __name__ == '__main__':
    db.create_all()
    manager.run()

