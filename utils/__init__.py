import os
import time
import datetime

from flask import (Flask, jsonify, request, abort)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
import telebot

token = "1721163869:AAGwE_mvTiwzITGsYK9najKI2U2yKLv5MHY"
WEBHOOK_URL_BASE = 'https://amurodov2005.pythonanywhere.com/'
WEBHOOK_URL_PATH = token
app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
bot = telebot.TeleBot(token, threaded=False)
manager.add_command('db', MigrateCommand)
# Admin
admin = Admin(app, name='Ramadan', template_mode='bootstrap3', url='/adminpanel')

# Configs
app.config['SECRET_KEY'] = 'sekretcha'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join('.') + '/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'


# Models
class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    different = db.Column(db.Integer)

    def __str__(self):
        return f"{self.name}"


class Day(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(255), nullable=False)
    saharlik = db.Column(db.DateTime)
    iftorlik = db.Column(db.DateTime)

    def __str__(self):
        return f"{self.name}"


def get_data(data=None):
    if data == 'region':
        regions = list(Region.query.all())
        return jsonify([(i.name, i.different) for i in regions])
    elif data == 'day':
        days = list(Day.query.all())
        return jsonify([(i.id, i.day, i.saharlik.strftime("%H:%M"), i.iftorlik.strftime("%H:%M")) for i in days])


# Admin Connection
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(Day, db.session))


# Views
@app.route('/' + WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)






