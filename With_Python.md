# With Python
## **super simple full system using Python Flask + MySQL** 

* RBAC authentication via JWT
* Admin dashboard showing paginated users from MySQL (500k+ rows assumed)
* Stress test using Locust
* SQL performance test can be done with MySQL tools (like `mysqlslap`)

---

### 1. Prepare MySQL Database

```sql
CREATE DATABASE dashboard_db;

USE dashboard_db;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  role VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert 600,000 dummy users (can be slow, use a script or stored procedure)
DELIMITER $$

CREATE PROCEDURE populate_users()
BEGIN
  DECLARE i INT DEFAULT 1;
  WHILE i <= 600000 DO
    INSERT INTO users (name, email, role) VALUES (
      CONCAT('User', i),
      CONCAT('user', i, '@example.com'),
      IF(i % 10 = 0, 'admin', 'user')
    );
    SET i = i + 1;
  END WHILE;
END$$

DELIMITER ;

CALL populate_users();
```

---

### 2. Flask App (`app.py`)

```python
from flask import Flask, request, jsonify, render_template
import mysql.connector
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

db_config = {
    'user': 'root',
    'password': 'yourpassword',
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
    cursor.execute("SELECT id, role FROM users WHERE email = %s", (email,))
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
```

---

### 3. Frontend `templates/dashboard.html`

```html
<!DOCTYPE html>
<html>
<head>
  <title>Admin Dashboard</title>
</head>
<body>
  <h1>User List</h1>
  <table border="1" id="userTable">
    <thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
    <tbody></tbody>
  </table>

  <script>
    const token = "PASTE_YOUR_JWT_HERE";

    fetch('/api/users?page=1&limit=50', {
      headers: { 'Authorization': 'Bearer ' + token }
    })
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector("#userTable tbody");
      data.forEach(user => {
        const row = `<tr><td>${user.id}</td><td>${user.name}</td><td>${user.email}</td></tr>`;
        tbody.innerHTML += row;
      });
    });
  </script>
</body>
</html>
```

---

### 4. Locust stress test (`locustfile.py`)

```python
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_users(self):
        self.client.get("/api/users?page=1&limit=50", headers={"Authorization": "Bearer PASTE_YOUR_JWT_HERE"})
```

Run locust with:

```bash
locust -f locustfile.py --host=http://127.0.0.1:5000
```

Open `http://localhost:8089` to simulate 10, 100, 1000 users.

---

### 5. SQL Performance Test with MySQL

You can run:

```bash
mysqlslap --concurrency=10 --iterations=20 --query="SELECT id, name, email FROM users LIMIT 50 OFFSET 0;" --create-schema=dashboard_db --user=root --password=yourpassword
```

Change `--concurrency` to test different user loads.

---

## Summary

* Minimal Flask app with JWT + RBAC
* MySQL with 600,000+ rows users table
* Admin dashboard with paginated user data
* Locust script to stress test dashboard API
* Use `mysqlslap` for SQL query performance test


| Requirement                     | Status                 | Notes                                              |
| ------------------------------- | ---------------------- | -------------------------------------------------- |
| Tech stack                      | ✅                      | Python Flask + MySQL                               |
| DB > 500k rows                  | ✅                      | 600k users script included                         |
| Auth & RBAC                     | ✅                      | JWT + role check decorator                         |
| Dashboard showing table         | ✅                      | `/dashboard` + `/api/users`                        |
| Stress test dashboard           | ✅                      | Locust script included                             |
| Pagination & without pagination | ✅ (default pagination) | Pass large limit param for no pagination           |
| Test 10,100,1000 users          | ✅                      | Locust configurable user count                     |
| SQL performance testing         | ✅                      | Use `mysqlslap`                                    |
| Query optimization & comparison | ➖                      | You can add indexes manually and test with EXPLAIN |
