from flask import Flask
from flask_sqlalchemy import SQLAlchemy

PASSWORD = input('Postgres password please: ')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://brown:{PASSWORD}@localhost:5432/example'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

db.create_all()

#@app.route('/')
#def index():
#    user = Person.query.first()
#    return 'Hello ' + user.name

if __name__ == '__main__':
    #app.debug = True
    #app.run(host='0.0.0.0')


    # create users in the database
    #users = [{'id': 1, 'name': 'Jacob'}, {'id': 2, 'name': 'Miso'}, {'id': 3, 'name': 'Bob'}]
    #for user in users:
    #    u = Users(id = user['id'], name = user['name'])
    #    db.session.add(u)
    #db.session.commit()

    all_bobs = Users.query.filter(Users.name == 'Bob').all()
    all_bs = Users.query.filter(Users.name.like('%b%')).all()
    number_bobs = Users.query.filter(Users.name == 'Bob').count()

    print(all_bobs, all_bs, number_bobs)