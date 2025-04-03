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

# Student-facing page to view and add/drop courses
@app.route('/add_courses', methods=['GET', 'POST'])
def add_courses():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    if request.method == 'POST':
        course_id = request.form['course']
        flash(f'Course {course_id} submitted successfully!')
        return redirect(url_for('add_courses'))

    return render_template('add_courses.html', courses=courses)

# General course viewing page
@app.route('/courses', methods=['GET', 'POST'])
def courses():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    if request.method == 'POST':
        course_id = request.form['course']
        flash(f'Course {course_id} submitted successfully!')
        return redirect(url_for('courses'))

    return render_template('courses.html', courses=courses)

# Admin panel
@app.route('/admin')
def admin_panel():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role = 'instructor'")
    instructors = cursor.fetchall()

    return render_template('admin.html', courses=courses, instructors=instructors)

# Instructor dashboard
@app.route('/instructor')
def instructor_dashboard():
    cursor.execute("SELECT * FROM courses WHERE InstructorID IS NOT NULL")
    courses = cursor.fetchall()
    return render_template('instructor.html', courses=courses)

# Empty for now
@app.route('/grades')
def grades():
    return render_template('grades.html')

# Placeholder to avoid error in navbar/admin actions
@app.route('/edit_course/<int:course_id>')
def edit_course(course_id):
    return f"Edit course {course_id} - Functionality coming soon."

@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    return f"Delete course {course_id} - Functionality coming soon."

@app.route('/submit', methods=['POST'])
def submit():
    return redirect(url_for('courses'))

@app.route('/view_students/<int:course_id>')
def view_students(course_id):
    return f"Viewing students for course {course_id} - Functionality coming soon."

if __name__ == '__main__':
    app.run(debug=True)
