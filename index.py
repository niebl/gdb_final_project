from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import psycopg2
import json

app = Flask(__name__)

# Database connection details
DB_CONFIG = {
    'dbname': 'gdb_db',
    'user': 'gdb',
    'password': 'gdb',
    'host': 'localhost',
    'port': 5432
}

@app.route('/')
def index():
    return render_template('index.html')

# SQL execution endpoint
@app.route('/execute-sql', methods=['POST'])
def execute_sql():
    try:
        # Get the SQL query from the request
        data = request.json
        query = data.get('query', '')

        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()

        # Get column names
        colnames = [desc[0] for desc in cursor.description]

        # Convert rows to GeoJSON if it's spatial data
        try:
            features = []
            for row in rows:
                # Assuming the last column is a GeoJSON geometry (adjust as needed)
                properties = {colnames[i]: row[i] for i in range(len(colnames) - 1)}
                geometry = json.loads(row[-1])  # Last column should be GeoJSON geometry
                features.append({
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": properties
                })

            # Close the connection
            cursor.close()
            conn.close()

            # Return the result as GeoJSON
            return jsonify(features)

        except:
            #this is in case no geojson formatted geometry was returned in the last col
            # Close the connection
            cursor.close()
            conn.close()

            return jsonify(rows)


    except Exception as e:
        print(e)
        data = request.json
        query = data.get('query', '')
        print(query)
        return jsonify({"error": str(e)}), 500