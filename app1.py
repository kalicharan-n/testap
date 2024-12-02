from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)
DB_PATH = "app.db"

# Helper function to interact with the database
def execute_query(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# Home page with metrics selection
@app.route('/')
def main_screen():
    metrics = fetch_query("SELECT name FROM metrics")
    return render_template('main_screen.html', metrics=metrics)


@app.route('/mapping-settings', methods=['GET', 'POST'])
def mapping_settings():
    error = None
    if request.method == 'POST':
        mapping_id = request.form.get('mapping_id')
        domain = request.form['domain']
        project = request.form['project']
        app_name = request.form['app_name']

        # Check for duplicates
        existing = fetch_query(
            "SELECT id FROM mapping WHERE domain = ? AND project = ? AND app_name = ?",
            (domain, project, app_name)
        )
        if existing and (not mapping_id or int(mapping_id) != existing[0][0]):
            error = "This mapping already exists. Please delete it before adding again."
        else:
            if mapping_id:
                # Update existing mapping
                execute_query(
                    "UPDATE mapping SET domain = ?, project = ?, app_name = ? WHERE id = ?",
                    (domain, project, app_name, mapping_id)
                )
            else:
                # Add new mapping
                execute_query(
                    "INSERT INTO mapping (domain, project, app_name) VALUES (?, ?, ?)",
                    (domain, project, app_name)
                )
        if not error:
            return redirect('/mapping-settings')

    mappings = fetch_query("SELECT domain, project, app_name, id FROM mapping")
    return render_template('mapping_settings.html', mappings=mappings, error=error)


# Metrics mapping page
@app.route('/metrics-mapping', methods=['GET', 'POST'])
def metrics_mapping():
    error = None
    if request.method == 'POST':
        metric_id = request.form.get('metric_id')
        metric_name = request.form['metric_name']
        api_endpoint = request.form['api_endpoint']
        headers = request.form.get('headers', '')
        body = request.form.get('body', '')

        try:
            # Insert or update metric
            if metric_id:
                execute_query(
                    "UPDATE metrics SET name = ?, endpoint = ?, headers = ?, body = ? WHERE id = ?",
                    (metric_name, api_endpoint, headers, body, metric_id)
                )
            else:
                execute_query(
                    "INSERT INTO metrics (name, endpoint, headers, body) VALUES (?, ?, ?, ?)",
                    (metric_name, api_endpoint, headers, body)
                )
        except Exception as e:
            error = f"An error occurred: {e}"

    # Retrieve all metrics for display
    metrics = fetch_query("SELECT id, name, endpoint, headers, body FROM metrics")
    return render_template('metrics_mapping.html', metrics=metrics, error=error)

# Dummy API endpoints
@app.route('/api/domains')
def api_domains():
    return jsonify(["Domain1", "Domain2", "Domain3"])

@app.route('/api/projects/<domain>')
def api_projects(domain):
    return jsonify(["Project1", "Project2", "Project3"])

@app.route('/api/app-names')
def api_app_names():
    return jsonify(["AppName1", "AppName2", "AppName3"])


# Delete mapping
@app.route('/delete-mapping/<int:id>')
def delete_mapping(id):
    execute_query("DELETE FROM mapping WHERE id = ?", (id,))
    return redirect('/mapping-settings')

# Delete metric
@app.route('/delete-metric/<int:metric_id>', methods=['GET'])
def delete_metric(metric_id):
    try:
        execute_query("DELETE FROM metrics WHERE id = ?", (metric_id,))
    except Exception as e:
        return redirect(f"/metrics-mapping?error={e}")
    return redirect('/metrics-mapping')

# Edit metric (not implemented fully for simplicity)
@app.route('/edit-metric/<int:id>', methods=['GET', 'POST'])
def edit_metric(id):
    if request.method == 'POST':
        # Update the metric in the database
        metric_name = request.form['metric_name']
        api_endpoint = request.form['api_endpoint']
        headers = request.form.get('headers', '')
        body = request.form.get('body', '')

        try:
            execute_query(
                "UPDATE metrics SET name = ?, endpoint = ?, headers = ?, body = ? WHERE id = ?",
                (metric_name, api_endpoint, headers, body, id)
            )
            return redirect('/metrics-mapping')
        except Exception as e:
            error = f"Error updating metric: {e}"
            return render_template('metrics_mapping.html', metrics=fetch_query("SELECT * FROM metrics"), error=error)

    # Fetch the metric data for GET requests
    metric = fetch_query("SELECT id, name, endpoint, headers, body FROM metrics WHERE id = ?", (id,))
    if not metric:
        return redirect('/metrics-mapping?error=Metric not found')

    metric_data = metric[0]  # Fetch the first (and only) result
    return jsonify({
        'id': metric_data[0],
        'name': metric_data[1],
        'endpoint': metric_data[2],
        'headers': metric_data[3],
        'body': metric_data[4]
    })


if __name__ == "__main__":
    app.run(debug=True)
