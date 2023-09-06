from some_info import password
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

PASSWORD = password

# __name__ is name of the file
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://brown:{PASSWORD}@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# route to listen to todos/create. requests that come in with the method "post"
@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False
    body = {}
    try:
        # get the todo item from the form
        # gets the json body that was sent to the request
        description = request.get_json()['description']

        # add the todo to the database table
        todo = Todo(description = description)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
    except:
        error=True
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()

    if error:
        abort (400)
    else:
        # update page with the new todo item
        #return redirect(url_for('index'))
        return jsonify(body)



# listens to home page        
@app.route('/')
def index():
    return render_template('index.html', data = Todo.query.all())

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')