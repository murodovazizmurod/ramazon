import os

from flask import (Flask, jsonify)
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

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


# Admin Connection
admin.add_view(ModelView(Region, db.session))
admin.add_view(ModelView(Day, db.session))


# Views

@app.route('/regions')
def region():
    regions = list(Region.query.all())
    if regions:
        return jsonify({'data': [(i.name, i.different) for i in regions], "status": 'ok'})
    else:
        return jsonify({"data": "No regions was found!", "status": "404"})


@app.route('/days')
def dates():
    days = list(Day.query.all())
    if days:
        return jsonify(
            {'data': [(i.id, i.day, i.saharlik.strftime("%H:%M"), i.iftorlik.strftime("%H:%M")) for i in days],
             "status": 'ok'})
    else:
        return jsonify({"data": "No data was found!", "status": "404"})


if __name__ == "__main__":
    app.run(debug=True)
