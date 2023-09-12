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

# individual todo items
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable = False)


    def __repr__(self):
        return f'<Todo {self.id} {self.description}>'

# todo lists to group the individual items
class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable = False)
    todos = db.relationship('Todo', backref = 'list', lazy = True)

    def __rep__(self):
        return f'<TodoList {self.id} {self.name}'

# ***** BEGIN INDIVIDUAL TODO HANDLERS ******

# handler to listen to todos/create. requests that come in with the method "post"
@app.route('/todos/create', methods=['POST'])
def create_todo():
    print('hello')
    error = False
    body = {}
    try:
        # get the todo item from the form
        # gets the json body that was sent to the request
        temp_dictionary = request.get_json()
        print(temp_dictionary)
        description = temp_dictionary['description']
        list_id = temp_dictionary['list_id']
        print(description, list_id)

        # add the todo to the database table. defaults completed to False
        todo = Todo(description = description, list_id = list_id, completed = False)
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description
        body['id'] = todo.id
        body['list_id'] = todo.list_id
    except:
        error=True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)

@app.route('/todos/<todo_id>/set-completed', methods=["POST"])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()

    return redirect(url_for('index'))

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exec_info())
    finally:
        db.session.close()

    return jsonify({ 'success': True })

# ***** BEGIN LIST TODO HANDLERS *****

# handler to create new list
@app.route('/lists/create', methods=["POST"])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        todo_list = TodoList(name = name)
        db.session.add(todo_list)
        db.session.commit()
        body['name'] = name
        body['id'] = todo_list.id
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)

# handler to set the new list items as completed
@app.route('/lists/<list_id>/set-completed', methods=["POST"])
def set_completed_list(list_id):
    error = False
    try:
        # get the children from the list and then set them to completed
        todos_list = TodoList.query.get(list_id)
        children = todos_list.todos

        for child in children:
            child.completed = True

        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()

    if error:
        abort(500)
    else:
        return '', 200

# handler to delete the new list items
@app.route('/lists/<list_id>/delete-me', methods=["DELETE"])
def delete_me_list(list_id):
    error = False
    try:
        todos_list = TodoList.query.get(list_id)
        children = todos_list.todos
        if children:
            for child in children:
                db.session.delete(child)
        db.session.delete(todos_list)
        db.session.commit()
    except:
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()

    if error:
        return jsonify({'success': False})
    else:
        # get the list with the greatest id and then pass that back so that page can be loaded
        return_list = TodoList.query.order_by('id').all()[-1]
        return_list_id = return_list.id
        print(return_list_id)

        return jsonify({'success': True, 'new_page_id': return_list_id}) 







# handler to load lists
@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template(
        'index.html',
        lists = TodoList.query.all(),
        active_list = TodoList.query.get(list_id),
        todos = Todo.query.filter_by(list_id=list_id).order_by('id').all())

# home page. defaults to list_id=1
@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')