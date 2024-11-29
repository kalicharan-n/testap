import sqlite3
from flask import Flask, render_template, request, redirect, jsonify

app = Flask(__name__)

DB_PATH = 'database/app.db'

# Helper functions for database operations
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT,
            run_id TEXT,
            app_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metric_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_endpoint TEXT,
            parameters TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_all(table_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_row(table_name, columns, values):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?']*len(values))})"
    cursor.execute(query, values)
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def main_screen():
    mappings = fetch_all('mappings')
    metrics = fetch_all('metric_config')
    return render_template('main_screen.html', mappings=mappings, metrics=metrics)

@app.route('/mapping', methods=['GET', 'POST'])
def mapping_screen():
    if request.method == 'POST':
        project = request.form['project']
        run_id = request.form['run_id']
        app_name = request.form['app_name']
        insert_row('mappings', ['project', 'run_id', 'app_name'], [project, run_id, app_name])
        return redirect('/mapping')
    mappings = fetch_all('mappings')
    return render_template('mapping_screen.html', mappings=mappings)

@app.route('/metric-config', methods=['GET', 'POST'])
def metric_config_screen():
    if request.method == 'POST':
        api_endpoint = request.form['api_endpoint']
        parameters = request.form['parameters']
        insert_row('metric_config', ['api_endpoint', 'parameters'], [api_endpoint, parameters])
        return redirect('/metric-config')
    configs = fetch_all('metric_config')
    return render_template('metric_config_screen.html', configs=configs)

@app.route('/trigger', methods=['POST'])
def trigger_flow():
    selected_metrics = request.form.getlist('metrics')
    app_name = request.form['app_name']
    # Logic to fetch metrics and push to InfluxDB can be added here.
    return jsonify({'status': 'Flow triggered successfully!', 'app_name': app_name, 'metrics': selected_metrics})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
