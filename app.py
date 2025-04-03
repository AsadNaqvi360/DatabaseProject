from flask import Flask, render_template
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    database=DB_CONFIG['database']
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
