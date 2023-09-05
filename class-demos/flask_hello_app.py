from flask import Flask
from flask_sqlalchemy import SQLAlchemy

PASSWORD = input('Postgres password please: ')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://brown:{PASSWORD}@localhost:5432/example'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# instantiate before creating the class?
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Person ID: {self.id}, name: {self.name}>'

# instantiates all db.Model classes. They then get stored as tables in the provided database
# subsequent instantiations of the class will create a row in the table that is created below
db.create_all()


@app.route('/')
def index():
    person = Person.query.first()
    return 'Hello ' + person.name

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')