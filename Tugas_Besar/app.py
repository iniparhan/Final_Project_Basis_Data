from flask import Flask, request, jsonify, render_template
import mysql.connector
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'dashboard_db',
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def token_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split()[1]
            
            if not token:
                return jsonify({'message': 'Token is missing!'}), 403
            
            try:
                data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
                if role and data['role'] != role:
                    return jsonify({'message': 'Permission denied'}), 401
            except Exception:
                return jsonify({'message': 'Token is invalid!'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route('/login', methods=['POST'])
def login():
    
    email = request.json.get('email')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT users.id, roles.name FROM users JOIN roles ON users.role_id = roles.id WHERE users.email = %s", (email,))
    
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user:
        return jsonify({"message": "Invalid user"}), 401
    
    token = jwt.encode({'id': user[0], 'role': user[1]}, app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({'token': token})

@app.route('/dashboard')
@token_required(role='admin')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/users')
@token_required(role='admin')
def api_users():
    
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{'id': u[0], 'name': u[1], 'email': u[2]} for u in users])

if __name__ == '__main__':
    app.run(debug=True)