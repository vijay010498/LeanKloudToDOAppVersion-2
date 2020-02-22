from flask import Flask, request, jsonify, make_response
from flask_mysqldb import MySQL
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt 
import datetime
from datetime import date
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c;=?gY,SKR)91:9c\'ODkDnL]smyk"t'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Vijay123'
app.config['MYSQL_DB']='ToDoList'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
    
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is Missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            cur = mysql.connection.cursor()
            mysql_query = '''SELECT * FROM User where public_id = %s'''
            cur.execute(mysql_query, [data['public_id']])
            current_user = cur.fetchone()   
        except:
            return jsonify({'Message' : 'Token is invalid'}), 401
        return f(current_user, *args, **kwargs)      
    return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'}) 
    cur = mysql.connection.cursor()
    mysql_query = '''select * from User'''
    cur.execute(mysql_query)
    users = cur.fetchall() 
    return jsonify({'users' : users})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query = '''select * from User where public_id = %s'''
    cur.execute(mysql_query, [public_id])
    user = cur.fetchall()
    if not user:
        return jsonify({'Message' : 'No user Found'})
    return jsonify({'users' : user})
    
@app.route('/user', methods=['POST'])
@token_required
def create_user(current_user):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    data = request.get_json()
    public_id=str(uuid.uuid4())
    name=data['name']
    hashed_password = generate_password_hash(data['password'], method='sha256')
    cur = mysql.connection.cursor()
    mysql_query = '''INSERT INTO User(public_id, name, password, admin) values(%s, %s, %s, %s)'''
    recordTuple = (public_id, name, hashed_password, 0 )
    cur.execute(mysql_query, recordTuple)
    mysql.connection.commit()
    return jsonify({'Message' : 'New User Created!'})
    
@app.route('/user/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query1 = '''select * from User where public_id = %s'''
    cur.execute(mysql_query1, [public_id])
    user = cur.fetchall()
    if not user:
        return jsonify({'Message' : 'No user Found'})
    mysql_query2 = '''update User set admin = %s where public_id = %s'''
    cur.execute(mysql_query2, [1,public_id])
    mysql.connection.commit()
    return jsonify({'Message' : 'The user has been promoted'})

@app.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query1 = '''select * from User where public_id = %s'''
    cur.execute(mysql_query1, [public_id])
    user = cur.fetchall()
    if not user:
        return jsonify({'Message' : 'No user Found'})
    mysql_query2 = '''delete from User where public_id = %s'''
    cur.execute(mysql_query2, [public_id])
    mysql.connection.commit()
    return jsonify({'Message' : 'The user has been deleted'})
    
@app.route('/login')
def login():
    auth =  request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401, {'www-Authenticate' : 'Basic realm="Login Required1"'})
    cur = mysql.connection.cursor()
    mysql_query1 = '''select * from User where name = %s'''
    cur.execute(mysql_query1, [auth.username])
    user = cur.fetchone()
    
    if not user:
        return make_response('Could not verify', 401, {'www-Authenticate' : 'Basic realm="Login Required1"'})
        
    if check_password_hash(user['password'], auth.password):
        token = jwt.encode({'public_id' : user['public_id'], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'www-Authenticate' : 'Basic realm="Login Required1"'})  

@app.route('/todo', methods=['GET'])
@token_required    
def get_all_todos(current_user):
    '''if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})'''
    cur = mysql.connection.cursor()
    mysql_query = '''SELECT * FROM TODO ORDER BY DUE_DATE ASC'''
    cur.execute(mysql_query)
    todo = cur.fetchall()
    if not todo:
        return jsonify({'Message' : 'NO TODO FOUND'})
    return jsonify({'TODO' : todo})
    
@app.route('/todo/<todo_id>', methods=['GET'])
@token_required
def get_one_todo(current_user, todo_id):
    '''if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})'''
    cur = mysql.connection.cursor()
    mysql_query = '''SELECT * FROM TODO WHERE ID = %s'''
    cur.execute(mysql_query, [todo_id])
    todo = cur.fetchall()
    if not todo:
        return jsonify({'Message' : 'No TODO FOUND'})
    return jsonify({'TODO' : todo})

@app.route('/todo', methods=['POST'])
@token_required
def create_todo(current_user):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    data = request.get_json()
    text = data['text']
    due_by = data['due_by']
    status = data['status']
    cur = mysql.connection.cursor()
    mysql_query = '''INSERT INTO TODO(Txt, DUE_DATE, STAT) VALUES(%s, %s, %s)'''
    recordTuple = (text, due_by, status)
    cur.execute(mysql_query, recordTuple)
    mysql.connection.commit() 
    return jsonify({'Message' : 'TODO CREATED !!'})
    
@app.route('/todo/<todo_id>', methods=['PUT'])
@token_required
def change_todo_status(current_user,todo_id):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query1 = '''SELECT * FROM TODO WHERE ID = %s'''
    cur.execute(mysql_query1, [todo_id])
    todo = cur.fetchall()
    if not todo:
        return jsonify({'MESSAGE' : 'NO TODO FOUND TO UPDATE'})
    data = request.get_json()
    status = data['status']
    mysql_query2 = '''UPDATE TODO SET STAT = %s WHERE ID = %s'''
    cur.execute(mysql_query2, [status, todo_id])
    mysql.connection.commit()
    return jsonify({'MESSAGE' : 'The todo status has been updated'})

@app.route('/todo/duedate/<due_date>', methods=['GET'])
@token_required
def get_todo_by_due_data(current_user,due_date):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query  = '''SELECT * FROM TODO WHERE DUE_DATE = %s'''
    cur.execute(mysql_query, [due_date])
    todo = cur.fetchall()
    if not todo:
        return jsonify({'MESSAGE' : 'NO TODO FOUND'})
    return jsonify({'TODO' : todo })

@app.route('/todo/overdue', methods=['GET'])
@token_required
def get_Over_Due(current_user):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    no_date = date.today()
    cur = mysql.connection.cursor()
    mysql_query = '''SELECT * FROM TODO WHERE DUE_DATE < CURRENT_DATE() '''
    cur.execute(mysql_query)
    todo = cur.fetchall()
    if not todo:
        return jsonify({'MESSAGE' : 'NO TODO FOUND !'})
    return  jsonify({'TODO' : todo})
    
@app.route('/todo/status/<status>',methods=['GET'])
@token_required
def get_todo_by_status(current_user, status):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query = '''select * from todo where stat = %s'''
    cur.execute(mysql_query, [status])
    todo = cur.fetchall()
    if not todo:
        return jsonify({'MESSAGE' : 'NO TODO FOUND WITH THAT STATUS'})
    return jsonify({'TODO' : todo})
    
    
@app.route('/todo/<todo_id>', methods=['DELETE'])
@token_required
def delete_todo(current_user,todo_id):
    if not current_user['admin']:
        return jsonify({'message' : 'cannot perform that function'})
    cur = mysql.connection.cursor()
    mysql_query1 = '''SELECT * FROM TODO WHERE ID = %s'''
    cur.execute(mysql_query1, [todo_id])
    todo = cur.fetchall()
    if not todo:
        return jsonify({'Message' : 'NO TODO FOUND!'})
    mysql_query2 = '''DELETE FROM TODO WHERE id = %s'''
    cur.execute(mysql_query2, [todo_id])
    mysql.connection.commit()
    return jsonify({'Message' : 'TODO HAS BEEN DELETED'})
    
if __name__=='__main__':
    app.run(debug=True)