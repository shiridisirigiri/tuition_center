from flask import Flask, render_template, request, redirect, url_for
import sqlite3

from flask import Flask, session

app = Flask(__name__)
app.secret_key = '8055'  # Set the secret key

@app.before_request
def set_role():
    session.setdefault('role', 'student')  # or 'student'

@app.route('/')
def index():
    if session.get('role') == 'admin':
        return render_template('admin/index.html', page="home")
    else:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM courses")
        courses = cur.fetchall()
        conn.close()
        return render_template('student/student_home.html', courses=courses, page="student_home")
    
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'dream' and password == '12345':
            session['role'] = 'admin'
            return redirect(url_for('index'))
        else:
            return "Invalid credentials", 401
    return render_template('admin/admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



@app.route('/students')
def students():
    course_filter = request.args.get('course')
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Filter students
    if course_filter:
        cur.execute("SELECT * FROM students WHERE course = ?", (course_filter,))
    else:
        cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    # Unique course list
    cur.execute("SELECT DISTINCT course FROM students")
    courses = cur.fetchall()

    # Total fees
    if course_filter:
        cur.execute("SELECT SUM(fees) FROM students WHERE course = ?", (course_filter,))
    else:
        cur.execute("SELECT SUM(fees) FROM students")
    total_fees = cur.fetchone()[0] or 0

    conn.close()
    return render_template('admin/students.html', students=students, courses=courses,
                           selected_course=course_filter, total_fees=total_fees, page="students")


@app.route('/courses')
def courses():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    conn.close()
    return render_template('admin/courses.html', courses=courses, page="courses")

@app.route('/available_courses')
def available_courses():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    conn.close()
    return render_template('student/courses.html', courses=courses)

from flask import flash

from flask import flash, session

@app.route('/add', methods=["GET", "POST"])
def add_student():
    if request.method == 'POST':
        name = request.form['name'].strip()
        course = request.form['course'].strip()
        fees = request.form['fees'].strip()

        if not name or not course or not fees:
            return "All fields are required!", 400

        try:
            fees = int(fees)
        except ValueError:
            return "Fees must be a number!", 400

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO students (name, course, fees) VALUES (?, ?, ?)", (name, course, fees))
        student_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Check role
        if session.get('role') == 'admin':
            flash("✅ Student added successfully!")
            return redirect(url_for('students'))
        else:
            session['student_id'] = student_id
            flash("🎉 Registration successful!")
            return redirect(url_for('student_home'))

    return render_template('admin/add_student.html')

from datetime import datetime  # Add this import at the top

@app.route('/addcourse', methods=["GET", "POST"])
def add_course():
    if request.method == 'POST':
        course_id = request.form['course_id'].strip()
        course_name = request.form['course_name'].strip()
        fees = request.form['fees'].strip()
        faculty_name = request.form['faculty_name'].strip()
        datetime_value = request.form.get('datetime', '').strip()
        duration = request.form['duration'].strip()

        if not course_id or not course_name or not fees or not faculty_name or not datetime_value or not duration:
            return "All fields are required!", 400  # show error message

        try:
            fees = int(fees)
            # Optional: validate datetime format (assumes 'YYYY-MM-DD HH:MM')
            parsed_datetime = datetime.strptime(datetime_value, "%Y-%m-%dT%H:%M")  # input type="datetime-local"
        except ValueError:
            return "Invalid fees or datetime format!", 400

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO courses (course_id, course_name, fees, faculty_name, datetime_value, duration) VALUES (?, ?, ?, ?, ?, ?)",
                    (course_id, course_name, fees, faculty_name, datetime_value, duration))
        conn.commit()
        conn.close()
        return redirect(url_for('courses'))

    return render_template('admin/add_course.html')


@app.route('/delete/<int:id>', methods=["POST"])
def delete_student(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('students'))
@app.route('/delete_course/<int:course_id>', methods=["POST"])
def delete_course(course_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE course_ID = ?", (course_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('courses'))

@app.route('/edit/<int:id>', methods=["GET", "POST"])
def edit_student(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form['name']
        course = request.form['course']
        fees = request.form['fees']
        cur.execute("UPDATE students SET name = ?, course = ?, fees = ? WHERE id = ?", (name, course, fees, id))
        conn.commit()
        conn.close()
        return redirect(url_for('students'))
    else:
        cur.execute("SELECT * FROM students WHERE id = ?", (id,))
        student = cur.fetchone()
        conn.close()
        return render_template('admin/edit_student.html', student=student)
@app.route('/edit_course/<int:course_id>', methods=["GET", "POST"])
def edit_course(course_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    if request.method == "POST":
        course_name = request.form.get('course_name', '').strip()
        fees = request.form.get('fees', '').strip()
        faculty_name = request.form.get('faculty_name', '').strip()
        datetime_value = request.form.get('datetime_value', '').strip()
        duration = request.form.get('duration', '').strip()

        # Basic validation
        if not course_name or not fees or not faculty_name or not datetime_value or not duration:
            conn.close()
            return "All fields are required!", 400

        cur.execute("""
            UPDATE courses
            SET course_name = ?, fees = ?, faculty_name = ?, datetime_value = ?, duration = ?
            WHERE course_id = ?
        """, (course_name, fees, faculty_name, datetime_value, duration, course_id))

        conn.commit()
        conn.close()
        return redirect(url_for('courses'))

    else:
        cur.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
        course = cur.fetchone()
        conn.close()
        return render_template('admin/edit_course.html', course=course)


@app.route('/course/<int:course_id>')
def course_details(course_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    course = cur.fetchone()
    conn.close()

    if not course:
        return "Course not found", 404

    # Static or dynamic modules (can also be fetched from DB)
    modules = {
        1: ["Introduction to Data Science", "Python Basics", "Data Analysis", "Machine Learning", "Projects"],
        2: ["Variables & Datatypes", "Control Structures", "Functions", "Modules & Packages", "File Handling"]
    }

    return render_template("student/course_Details.html", course=course, modules=modules.get(course_id, []))


@app.route('/student_home')
def student_home():
    if 'student_id' in session:
        student_id = session['student_id']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # Fetch student details
        cur.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cur.fetchone()

        # Fetch courses to show (if needed on the student home page)
        cur.execute("SELECT * FROM courses")
        courses = cur.fetchall()

        conn.close()

        return render_template('student/student_home.html', student=student, courses=courses, page="student_home")
    else:
        return redirect(url_for('index'))







if __name__ == '__main__':
    app.run(debug=True)
