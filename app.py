from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DB setup
db = mysql.connector.connect(
    host="Naqvi.mysql.pythonanywhere-services.com",
    user="Naqvi",  # your PythonAnywhere username
    password="Happy657063!",  # <<< fill this in yourself
    database="Naqvi$infr"  # your full database name
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    return render_template('index.html')

# ----- STUDENT VIEW -----
@app.route('/student', methods=['GET', 'POST'])
def student_view():
    cursor.execute("SELECT * FROM courses")
    all_courses = cursor.fetchall()

    student_id = 1  # Hardcoded until login is added

    if request.method == 'POST':
        course_id = request.form['course_id']
        action = request.form['action']
        if action == 'Add':
            cursor.execute("INSERT INTO classschedules (StudentID, CourseID) VALUES (%s, %s)", (student_id, course_id))
            flash('Course added.')
        elif action == 'Drop':
            cursor.execute("DELETE FROM classschedules WHERE StudentID = %s AND CourseID = %s", (student_id, course_id))
            flash('Course dropped.')
        db.commit()
        return redirect(url_for('student_view'))

    cursor.execute("""
        SELECT c.CourseName FROM classschedules cs
        JOIN courses c ON cs.CourseID = c.CourseID
        WHERE cs.StudentID = %s
    """, (student_id,))
    registered = cursor.fetchall()

    cursor.execute("""
        SELECT c.CourseName, g.Grade FROM grades g
        JOIN courses c ON g.CourseID = c.CourseID
        WHERE g.StudentID = %s
    """, (student_id,))
    grades = cursor.fetchall()

    return render_template('student.html', all_courses=all_courses, registered=registered, grades=grades)

# ----- INSTRUCTOR VIEW -----
@app.route('/instructor', methods=['GET'])
def instructor_view():
    instructor_id = 2  # Simulated
    cursor.execute("SELECT * FROM courses WHERE InstructorID = %s", (instructor_id,))
    courses = cursor.fetchall()
    return render_template('instructor.html', courses=courses)

@app.route('/update_grade/<int:course_id>', methods=['POST'])
def update_grade(course_id):
    student_id = request.form['student_id']
    grade = request.form['grade']

    cursor.execute("""
        INSERT INTO grades (StudentID, CourseID, Grade)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE Grade = VALUES(Grade)
    """, (student_id, course_id, grade))
    db.commit()
    flash('Grade updated.')
    return redirect(url_for('instructor_view'))

# ----- ADMIN PANEL -----
@app.route('/admin', methods=['GET'])
def admin_panel():
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()
    cursor.execute("SELECT * FROM users WHERE role = 'instructor'")
    instructors = cursor.fetchall()
    return render_template('admin.html', courses=courses, instructors=instructors)

@app.route('/add_course', methods=['POST'])
def add_course():
    name = request.form['course_name']
    dept = request.form['department']
    credits = request.form['credits']
    instructor_id = request.form['instructor_id']

    cursor.execute("""
        INSERT INTO courses (CourseName, Department, Credits, InstructorID)
        VALUES (%s, %s, %s, %s)
    """, (name, dept, credits, instructor_id))
    db.commit()
    flash('Course added successfully.')
    return redirect(url_for('admin_panel'))

# ✅ NEWLY ADDED ROUTE
@app.route('/add_instructor', methods=['POST'])
def add_instructor():
    name = request.form['name']
    department = request.form['department']

    cursor.execute("""
        INSERT INTO users (Name, Department, role)
        VALUES (%s, %s, 'instructor')
    """, (name, department))
    db.commit()
    flash('Instructor added successfully.')
    return redirect(url_for('admin_panel'))

# Optional placeholders
@app.route('/edit_course/<int:course_id>')
def edit_course(course_id):
    return f"Edit functionality for Course ID {course_id} coming soon."

@app.route('/delete_course/<int:course_id>')
def delete_course(course_id):
    return f"Delete functionality for Course ID {course_id} coming soon."

@app.route('/view_students/<int:course_id>')
def view_students(course_id):
    return f"Viewing students in Course ID {course_id} coming soon."

if __name__ == '__main__':
    app.run(debug=True)
