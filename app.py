from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp, generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=3000)
app.secret_key = 'thisismysecre'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),unique=True, nullable=False)
    hashed_password = db.Column(db.String(),nullable=False)

    def __init__(self,username,password):
        self.username = username
        self.hashed_password = generate_password_hash(password, method='sha256')
        
    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_user(self):
        db.sessions.delete(self)
        db.session.commit()
      
    @classmethod #/auth
    def authenticate(cls, username, password):
        user = cls.find_by_username(username)
        if user and check_password_hash(user.hashed_password, password):
            print(user)
            return user

    @classmethod
    def identity(cls, payload):  
        user_id = payload['identity']
        return cls.query.get(int(user_id))
   

jwt = JWT(app, User.authenticate, User.identity)

  
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(180), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def __init__(self, text, user_id):
        self.text = text
        self.user_id = user_id
    
    @classmethod
    def get_all_todos_for_user(cls, user_id):
        todos = cls.query.filter_by(user_id=user_id).all()
        return todos
    
    @classmethod
    def get_todo_by_id(cls, id, user_id):
        todo = cls.query.filter_by(user_id=user_id, id=id).first()
        return todo
        
    
    def json(self):
        return {"text": self.text}
    
    def save_todo_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_todo(self):
        db.session.delete(self)
        db.session.commit()
    
@app.route('/signup',methods=['POST'])
def signup():
    data = request.get_json()
    if data and data['username'].strip() is None or data['password'].strip() is None:
        return jsonify({"description": "Invalid credentials",
            "error": "Bad Request", "status_code": 401}), 401
        
    user = User.find_by_username(data['username'].strip().lower())
    if user:
        return jsonify({"description": "User already exist",
            "error": "Bad Request", "status_code": 400}), 400
        
    
    new_user =  User(data['username'].lower().strip(), data['password'])
    new_user.save_to_db()
    return jsonify({"message": "User created successfully"}),201
    
@app.route('/todos')
@jwt_required()
def get_user_todos():
    user_id = current_identity.id
    todos = Todo.get_all_todos_for_user(user_id)
    
    return jsonify({"todos": [
        {
            "text":item.text,
            "id":item.id
        } for item in todos
    ]}), 200


@app.route('/todo/<string:id>',methods=['GET'])
@jwt_required()
def get_single_todo(id):
    user_id = current_identity.id
    todo = Todo.get_todo_by_id(id, user_id)
    if todo:
        return jsonify({
            "todo": {
                "text":todo.text,
                "id":todo.id
            }
        })
    return jsonify({"message": "Todo not found"}), 404

@app.route('/todo', methods=['POST'])
@jwt_required()
def create_todo():
    data = request.get_json()
    if data and not len(data['text'].strip()):
        return jsonify({"description": "Text should not be empty",
        "error": "Bad Request", "status_code": 401}), 401
    
    user_id = current_identity.id
    new_todo = Todo(data['text'], user_id)
    new_todo.save_todo_to_db()
    
    return jsonify(new_todo.json()), 201
 
    

@app.route('/todo/<string:id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
    data =  request.get_json()
    if data and not len(data['text'].strip()):
        return jsonify({"description": "Text should not be empty",
    "error": "Bad Request", "status_code": 401}), 401
    
    user_id = current_identity.id
    todo = Todo.get_todo_by_id(id, user_id)
    if todo is None:
        try:
            todo = Todo(data['text'], user_id)
       
        except Exception:
            return jsonify({"description": "Something went wrong",
                    "error": "Server internal error", "status_code": 500}), 500
    else:
        try:
            todo.text = data['text']
        except Exception:
            return jsonify({"description": "Something went wrong",
                    "error": "Server internal error", "status_code": 500}), 500
    
    todo.save_todo_to_db()
    return jsonify({"todo": {
           "text":todo.text,
            "id":todo.id
        }}), 201

@app.route('/todo/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_todo(id):
    try:
        user_id = current_identity.id
        todo = Todo.get_todo_by_id(id, user_id)
        todo.delete_todo()
        
        return {"message": "successfully deleted"}, 200
    except Exception:
        return {"description": "bad request",
        "error": "Bad Request", "status_code": 401}, 401

if __name__ == "__main__":
    app.run(debug=True)