from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# LoginManager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database connection
db = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    database=DB_CONFIG['database']
)
cursor = db.cursor(dictionary=True)

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user['id'], user['username'], user['role'])
    return None

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = 'student'  # Default role

        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                       (username, email, password, role))
        db.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['role'])
            login_user(user_obj)

            flash('Logged in successfully!')
            if user_obj.role == 'student':
                return redirect(url_for('dashboard'))
            elif user_obj.role == 'instructor':
                return redirect(url_for('instructor_dashboard'))
            elif user_obj.role == 'admin':
                return redirect(url_for('admin_panel'))

        flash('Invalid credentials.')
    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('index'))

# Student Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        flash('Access denied.')
        return redirect(url_for('index'))

    cursor.execute("""
        SELECT c.CourseName, cs.Day, cs.Time, g.Grade
        FROM grades g
        JOIN courses c ON g.CourseID = c.CourseID
        LEFT JOIN classschedules cs ON c.CourseID = cs.CourseID
        WHERE g.StudentID = %s
    """, (current_user.id,))
    
    courses = cursor.fetchall()
    return render_template('dashboard.html', courses=courses)

#Student Course Registration
def selectCourses(self):
        try:
            self.cur.execute("SELECT * FROM Courses")
            result = self.cur.fetchall()
        finally:
            self.cur.close()
        return result

app = Flask(__name__, template_folder='templates')

@app.route('/course_registration')
def listCourses():
    db = Database()
    courses = db.selectCourses()

    return render_template('courses.html', courses=courses)

#Student Schedule View

def get_student_schedule(self, student_id):
        try:
            sql = """
            SELECT s.StudentID, s.Name, c.CourseID, c.CourseName, c.Credits, c.InstructorID
            FROM Students s
            JOIN StudentCourses sc ON s.StudentID = sc.StudentID
            JOIN Courses c ON sc.CourseID = c.CourseID
            WHERE s.StudentID = %s
            """
            self.cur.execute(sql, (student_id,))
            result = self.cur.fetchall()
        finally:
            self.cur.close()
        return result

@app.route('/schedule', methods=['GET', 'POST'])
def view_schedule():
    schedule = None
    if request.method == 'POST':
        student_id = request.form['student_id']
        db = Database()
        schedule = db.get_student_schedule(student_id)
    return render_template('schedule.html', schedule=schedule)
# Instructor Dashboard
@app.route('/instructor')
@login_required
def instructor_dashboard():
    if current_user.role != 'instructor':
        flash('Access denied.')
        return redirect(url_for('index'))

    cursor.execute("""
        SELECT c.CourseName, c.CourseID
        FROM courses c
        WHERE c.InstructorID = %s
    """, (current_user.id,))
    
    courses = cursor.fetchall()
    return render_template('instructor.html', courses=courses)

# Admin Panel
@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Access denied.')
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    cursor.execute("SELECT * FROM users WHERE role = 'instructor'")
    instructors = cursor.fetchall()

    return render_template('admin.html', courses=courses, instructors=instructors)

# Run locally (optional, not used on PythonAnywhere)
if __name__ == '__main__':
    app.run(debug=True)
