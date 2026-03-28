from flask import Flask, request
import pymysql

# Create the Flask application
app = Flask(__name__)

# Database connection settings
# For now, values are hardcoded because this is still the manual MVP phase.
# Later, they should be moved to environment variables.
DB_HOST = "192.168.1.43"
DB_USER = "app_user"
DB_PASSWORD = "password"
DB_NAME = "app_db"

@app.route("/", methods=["GET"])
def form():
    """
    Display a very simple HTML form.
    This is the entry point of the MVP.
    """
    return """
        <h2>DevOps Foundation Lab</h2>
        <form method="POST" action="/submit">
            First name: <input name="first_name"><br><br>
            Last name: <input name="last_name"><br><br>
            <input type="submit" value="Send">
        </form>
    """

@app.route("/submit", methods=["POST"])
def submit():
    """
    Receive form data and insert it into the MariaDB database.
    """
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (first_name, last_name) VALUES (%s, %s)",
        (first_name, last_name)
    )
    conn.commit()
    conn.close()

    return "User added!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)