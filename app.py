from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# DB setup
db = mysql.connector.connect(
    host="Naqvi.mysql.pythonanywhere-services.com",
    user="Naqvi",
    password="Happy657063!",
    database="Naqvi$infr"
)
cursor = db.cursor(dictionary=True)

@app.route('/')
def index():
    return render_template('index.html')

# ----- STUDENT VIEW WITH SIMULATION -----
@app.route('/student', methods=['GET', 'POST'])
def student_view():
    cursor.execute("SELECT id, username FROM users WHERE role = 'student' AND username != 'student1'")
    students = cursor.fetchall()

    selected_student_id = request.args.get('student_id', default=students[0]['id'], type=int)

    cursor.execute("SELECT * FROM courses")
    all_courses = cursor.fetchall()

    if request.method == 'POST':
        selected_student_id = int(request.form['student_id'])
        course_id = request.form['course_id']
        action = request.form['action']
        if action == 'Add':
            cursor.execute("INSERT INTO classschedules (StudentID, CourseID) VALUES (%s, %s)", (selected_student_id, course_id))
            flash('Course added.')
        elif action == 'Drop':
            cursor.execute("DELETE FROM classschedules WHERE StudentID = %s AND CourseID = %s", (selected_student_id, course_id))
            flash('Course dropped.')
        db.commit()
        return redirect(url_for('student_view', student_id=selected_student_id))

    cursor.execute("""
        SELECT c.CourseName FROM classschedules cs
        JOIN courses c ON cs.CourseID = c.CourseID
        WHERE cs.StudentID = %s
    """, (selected_student_id,))
    registered = cursor.fetchall()

    cursor.execute("""
        SELECT c.CourseName, g.Grade
        FROM grades g
        JOIN courses c ON g.CourseID = c.CourseID
        WHERE g.StudentID = %s
    """, (selected_student_id,))
    grades = cursor.fetchall()

    return render_template('student.html',
        all_courses=all_courses,
        registered=registered,
        grades=grades,
        students=students,
        selected_student_id=selected_student_id
    )

# ----- INSTRUCTOR VIEW WITH SIMULATION -----
@app.route('/instructor', methods=['GET'])
def instructor_view():
    cursor.execute("SELECT id, username FROM users WHERE role = 'instructor' AND username != 'instructor1'")
    instructors = cursor.fetchall()
    selected_id = request.args.get('instructor_id', default=instructors[0]['id'], type=int)

    cursor.execute("SELECT * FROM courses WHERE InstructorID = %s", (selected_id,))
    courses = cursor.fetchall()

    for course in courses:
        cursor.execute("""
            SELECT u.id, u.username, g.Grade
            FROM classschedules cs
            JOIN users u ON cs.StudentID = u.id
            LEFT JOIN grades g ON g.StudentID = u.id AND g.CourseID = %s
            WHERE cs.CourseID = %s
        """, (course['CourseID'], course['CourseID']))
        course['students'] = cursor.fetchall()

    return render_template('instructor.html',
        courses=courses,
        instructors=instructors,
        selected_id=selected_id
    )

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
    cursor.execute("SELECT * FROM users WHERE role = 'instructor' AND username != 'instructor1'")
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

@app.route('/delete_course', methods=['POST'])
def delete_course():
    course_id = request.form['course_id']

    cursor.execute("DELETE FROM classschedules WHERE CourseID = %s", (course_id,))
    cursor.execute("DELETE FROM grades WHERE CourseID = %s", (course_id,))
    cursor.execute("DELETE FROM courses WHERE CourseID = %s", (course_id,))
    db.commit()
    flash('Course deleted successfully.')
    return redirect(url_for('admin_panel'))

@app.route('/add_instructor', methods=['POST'])
def add_instructor():
    name = request.form['name']
    department = request.form['department']

    cursor.execute("""
        INSERT INTO users (username, email, password, role)
        VALUES (%s, %s, %s, 'instructor')
    """, (name, f"{name.lower()}@example.com", 'defaultpass'))

    db.commit()
    flash('Instructor added successfully.')
    return redirect(url_for('admin_panel'))

# Optional
@app.route('/edit_course/<int:course_id>')
def edit_course(course_id):
    return f"Edit functionality for Course ID {course_id} coming soon."

@app.route('/view_students/<int:course_id>')
def view_students(course_id):
    return f"Viewing students in Course ID {course_id} coming soon."

if __name__ == '__main__':
    app.run(debug=True)
