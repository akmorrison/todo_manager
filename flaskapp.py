import flask
import json
from todo_items import *
app = flask.Flask(__name__)


@app.route('/')
def hello_world():
    return 'testtesttest'

@app.route('/short')
def short_list():
    return flask.jsonify(get_todos_for_api())

@app.route('/remove_item/<uid>')
def remove_item(uid):
    return remove_todo_by_uid(uid)

@app.route('/add_item', methods=['POST'])
def add_item():
    data = flask.request.json
    return new_item(data['item'], data['tags'], data['warn'], data['due'])

startup()

if __name__ == '__main__':
    app.run()
