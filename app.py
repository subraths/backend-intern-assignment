from flask import json
from werkzeug.exceptions import HTTPException
from flask import Flask
from flask_mysqldb import MySQL
from flask import request
from flask import jsonify
from markupsafe import escape
from os import environ

DB_HOST = environ.get("HOST")
DB_USER = environ.get("DB_USER")
DB_PASSWORD = environ.get("DB_PASSWORD")
DB_NAME = environ.get("DB_NAME")

app = Flask(__name__)
app.config["MYSQL_HOST"] = DB_HOST
app.config["MYSQL_USER"] = DB_USER
app.config["MYSQL_PASSWORD"] = DB_PASSWORD
app.config["MYSQL_DB"] = DB_NAME

mysql = MySQL(app)


@app.get("/")
def get_all_tasks():
    cursor = mysql.connection.cursor()
    try:
        query = "SELECT * FROM tasks"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        tasks = []
        for row in data:
            task = {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "due_date": str(row[3]),
            }
            tasks.append(task)
        return jsonify(tasks)
    except Exception as e:
        return f"an errrr {str(e)}"


@app.post("/")
def create_task():
    name = request.form["name"]
    description = request.form["description"]
    due_date = request.form["due_date"]
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(
            f"INSERT INTO tasks (name, description, due_date) VALUES ('{name}', '{description}', '{due_date}')"
        )
        mysql.connection.commit()
        cursor.fetchall()
        cursor.close()
        return jsonify({"message": "sicc"})
    except Exception as e:
        print(f"Error executing {str(e)}")
        return jsonify({"message": "failed", "err": str(e)}), 400


@app.route("/<id>", methods=("GET", "PATCH", "DELETE"))
def get_single_task(id):
    cursor = mysql.connection.cursor()

    if request.method == "GET":
        query = f"SELECT * from tasks WHERE ID = {id}"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        if data:
            tasks = []
            for row in data:
                task = {
                    "id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "due_date": str(row[3]),
                }
                tasks.append(task)
            return jsonify(tasks), 200
        return jsonify({"message": f"no task with id {id}"}), 404

    if request.method == "PATCH":
        name = request.form["name"]
        description = request.form["description"]
        due_date = request.form["due_date"]

        if not (name and description and due_date):
            return jsonify({"message": "please proide parameters"}), 400

        query = "UPDATE tasks SET"
        if name is not None:
            query += f" name='{name}',"

        if description is not None:
            query += f" description='{description}',"

        if due_date is not None:
            query += f" due_date='{due_date}',"

        query = query.rstrip(",")

        query += f" WHERE ID={id}"

        try:
            cursor.execute(query)
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "success"})
        except Exception as e:
            return jsonify({"message": "failed", "err": str(e)})

    if request.method == "DELETE":
        try:
            query = f"DELETE FROM tasks WHERE ID={id}"
            cursor.execute(query)
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "cic"})
        except Exception as e:
            return jsonify({"message": "failed", "error": f"str(e), check id"}), 400

    return jsonify({"message": "route not found"})


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response
