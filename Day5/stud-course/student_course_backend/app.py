from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# Init app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_course.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db + marshmallow
db = SQLAlchemy(app)
ma = Marshmallow(app)

# ---------- MODELS ----------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, nullable=False)

# Association table for many-to-many
enrollments = db.Table('enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)

# Add relationship
Student.courses = db.relationship('Course', secondary=enrollments, backref='students')

# ---------- SCHEMAS ----------
class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True

class CourseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        load_instance = True

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)
course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

# ---------- ROUTES ----------
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()
    new_student = Student(name=data["name"], email=data["email"])
    db.session.add(new_student)
    db.session.commit()
    return student_schema.jsonify(new_student)

@app.route("/students", methods=["GET"])
def get_students():
    students = Student.query.all()
    return students_schema.jsonify(students)

@app.route("/students/<int:id>", methods=["PUT"])
def update_student(id):
    student = Student.query.get_or_404(id)
    data = request.get_json()
    student.name = data.get("name", student.name)
    student.email = data.get("email", student.email)
    db.session.commit()
    return student_schema.jsonify(student)

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"})

@app.route("/courses", methods=["POST"])
def add_course():
    data = request.get_json()
    new_course = Course(code=data["code"], name=data["name"], credits=data["credits"])
    db.session.add(new_course)
    db.session.commit()
    return course_schema.jsonify(new_course)

@app.route("/courses", methods=["GET"])
def get_courses():
    courses = Course.query.all()
    return courses_schema.jsonify(courses)

@app.route("/enroll", methods=["POST"])
def enroll_student():
    data = request.get_json()
    student = Student.query.get_or_404(data["student_id"])
    course = Course.query.get_or_404(data["course_id"])
    student.courses.append(course)
    db.session.commit()
    return jsonify({"message": f"Enrolled {student.name} in {course.name}"})

@app.route("/students/<int:id>/courses", methods=["GET"])
def get_student_courses(id):
    student = Student.query.get_or_404(id)
    return courses_schema.jsonify(student.courses)

@app.route("/courses/<int:id>/students", methods=["GET"])
def get_course_students(id):
    course = Course.query.get_or_404(id)
    return students_schema.jsonify(course.students)

# ---------- MAIN ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
