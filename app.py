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

@app.route('/add_courses', methods=['GET', 'POST'])
def add_courses():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    if request.method == 'POST':
        course_id = request.form['course']
        flash(f'Course {course_id} submitted successfully!')
        return redirect(url_for('add_courses'))
    return render_template('add_courses.html', courses=courses)

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
    cursor.execute("SELECT * FROM courses WHERE InstructorID IS NOT NULL")
    courses = cursor.fetchall()
    return render_template('instructor.html', courses=courses)

@app.route('/grades')
def grades():
    # Placeholder until login is implemented
    flash("Login system not implemented. Can't fetch user grades.")
    return redirect(url_for('index'))

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

@app.route('/add_course', methods=['POST'])
def add_course():
    name = request.form['course_name']
    dept = request.form['department']
    credits = request.form['credits']
    instructor = request.form['instructor_id']
    cursor.execute("""
        INSERT INTO courses (CourseName, Department, Credits, InstructorID)
        VALUES (%s, %s, %s, %s)
    """, (name, dept, credits, instructor))
    db.commit()
    flash("Course added successfully.")
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
