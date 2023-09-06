from some_info import password
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

PASSWORD = password

# __name__ is name of the file
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://brown:{PASSWORD}@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# sets up flask db init and flask db migrate from the command line
#migrate = Migrate(app, db)

db.create_all()

# route to listen to todos/create. requests that come in with the method "post"
@app.route('/todos/create', methods=['POST'])
def create_todo():
    # get the todo item from the form
    description = request.form.get('description', '')

    # add the todo to the database table
    todo = Todo(description = description)
    db.session.add(todo)
    db.session.commit()

    # update page with the new todo item
    return redirect(url_for('index'))



# listens to home page        
@app.route('/')
def index():
    return render_template('index.html', data = Todo.query.all())

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')