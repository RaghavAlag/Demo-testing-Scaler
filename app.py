from flask import Flask, request, jsonify
import sqlite3
import os
import database

app = Flask(__name__)

# Initialize Enterprise DB
database.init_db()

def get_db():
    conn = sqlite3.connect('enterprise.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET'])
def home():
    return """
    <html>
        <head>
            <title>Enterprise Employee Portal</title>
            <style>
                body { font-family: sans-serif; padding: 50px; background: #f0f2f5; }
                .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Enterprise Management Console (Internal)</h1>
            
            <div class="card">
                <h3>Employee Directory Search</h3>
                <p>Search by name to view department details.</p>
                <form action="/api/v1/search" method="POST">
                    <input type="text" name="search_term" placeholder="Employee Name..." />
                    <button type="submit">Search</button>
                </form>
            </div>
            
            <div class="card">
                <h3>System Health Check</h3>
                <p>Enter a server address to verify connectivity.</p>
                <form action="/api/v1/diagnostics" method="POST">
                    <input type="text" name="endpoint" placeholder="127.0.0.1" />
                    <button type="submit">Run Check</button>
                </form>
            </div>
        </body>
    </html>
    """

@app.route('/api/v1/search', methods=['POST'])
def search_employees():
    data = request.json if request.is_json else request.form
    name = data.get('search_term', '')
    
    # VULNERABILITY: SQL Injection via string formatting
    query = "SELECT * FROM employees WHERE full_name = '" + name + "'"
    
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        if results:
            return jsonify({"status": "success", "data": [dict(r) for r in results]})
        return jsonify({"status": "fail", "message": "No employee found."})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route('/api/v1/diagnostics', methods=['POST'])
def diagnostics():
    data = request.json if request.is_json else request.form
    target = data.get('endpoint', '')
    
    # VULNERABILITY: OS Command Injection
    cmd = "ping -n 1 " + target
    
    try:
        process = os.popen(cmd)
        output = process.read()
        return jsonify({"status": "complete", "raw_output": output})
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "port": 5001})

if __name__ == '__main__':
    print("Enterprise Target running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001)