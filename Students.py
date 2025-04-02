# A very simple Flask Hello World app for you to get started with...
#MySQL password = eLeRsTup
from flask import Flask, render_template
import pymysql
import credentials

class  Database:
    def __init__(self):
        host = credentials.DB_HOST
        user = credentials.DB_USER
        pwd = credentials.DB_PWD
        db = credentials.DB_NAME

        self.con = pymysql.connect(host=host, user=user, password=pwd, db=db, cursorclass=pymysql.cursors.DictCursor)
        self.cur=self.con.cursor()

    def selectCourses(self):
        try:
            self.cur.execute("SELECT * FROM Courses")
            result = self.cur.fetchall()
        finally:
            self.cur.close()
        return result

app = Flask(__name__, template_folder='templates')

@app.route('/Registration')
def listCourses():
    db = Database()
    courses = db.selectCourses()

    return render_template('courses.html', courses=courses)