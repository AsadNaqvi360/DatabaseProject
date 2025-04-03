from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        item_name = request.form['item_name']
        supplier = request.form['supplier']
        date_received = request.form['date_received']
        description = request.form['description']
        cost = request.form['cost']
        quantity = request.form['quantity']

        cursor.execute("""
            INSERT INTO inventory (item_name, supplier, date_received, description, cost, quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (item_name, supplier, date_received, description, cost, quantity))
        db.commit()
        flash('Item added successfully!')
        return redirect(url_for('add'))

    return render_template('add.html')

@app.route('/courses', methods=['GET', 'POST'])
def courses():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    if request.method == 'POST':
        course_id = request.form['course']
        flash(f'Course {course_id} submitted successfully!')
        return redirect(url_for('courses'))

    return render_template('courses.html', courses=courses)

@app.route('/admin')
def admin_panel():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role = 'instructor'")
    instructors = cursor.fetchall()

    return render_template('admin.html', courses=courses, instructors=instructors)

@app.route('/instructor')
def instructor_dashboard():
    # Replace this with proper filtering if you have session/auth logic later
    cursor.execute("SELECT * FROM courses WHERE InstructorID IS NOT NULL")
    courses = cursor.fetchall()
    return render_template('instructor.html', courses=courses)

@app.route('/grades')
def grades():
    return render_template('grades.html')

# Placeholder routes used in admin.html to avoid URL errors
@app.route('/edit_course/<int:course_id>')
def edit_course(course_id):
    return f"Edit page for course {course_id} (not implemented yet)"

@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    return f"Delete confirmation for course {course_id} (not implemented yet)"

@app.route('/submit', methods=['POST'])
def submit():
    return redirect(url_for('courses'))

@app.route('/view_students/<int:course_id>')
def view_students(course_id):
    return f"View students for course {course_id} (not implemented yet)"

if __name__ == '__main__':
    app.run(debug=True)
