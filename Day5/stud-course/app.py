from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQLite DB file in the instance folder by default for sqlite:///site.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Association table for many-to-many Student<->Course
enrollments = db.Table(
    'enrollments',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    # Many-to-many relationship to Course via association table
    courses = db.relationship('Course', secondary=enrollments, back_populates='students')

    def to_dict(self, include_courses=False):
        data = {
            "id": self.id,
            "name": self.name,
            "student_id": self.student_id
        }
        if include_courses:
            data["courses"] = [c.to_dict() for c in self.courses]
        return data

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    # Many-to-many back-population
    students = db.relationship('Student', secondary=enrollments, back_populates='courses')

    def to_dict(self, include_students=False):
        data = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "credits": self.credits
        }
        if include_students:
            data["students"] = [s.to_dict() for s in self.students]
        return data

# One-time DB initialization (run separately or in Python shell)
# with app.app_context():
#     db.create_all()

# -------------------------------
# Student CRUD
# -------------------------------
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json() or {}
    if not all(k in data for k in ('name', 'student_id')):
        abort(400, description="Missing required fields: name, student_id")
    student = Student(name=data['name'], student_id=data['student_id'])
    db.session.add(student)
    db.session.commit()
    return jsonify(student.to_dict()), 201

@app.route('/students', methods=['GET'])
def list_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@app.route('/students/<int:sid>', methods=['GET'])
def get_student(sid):
    student = Student.query.get_or_404(sid)
    return jsonify(student.to_dict(include_courses=True))

@app.route('/students/<int:sid>', methods=['PUT'])
def update_student(sid):
    student = Student.query.get_or_404(sid)
    data = request.get_json() or {}
    if 'name' in data:
        student.name = data['name']
    if 'student_id' in data:
        student.student_id = data['student_id']
    db.session.commit()
    return jsonify(student.to_dict(include_courses=True))

@app.route('/students/<int:sid>', methods=['DELETE'])
def delete_student(sid):
    student = Student.query.get_or_404(sid)
    db.session.delete(student)
    db.session.commit()
    return '', 204

# -------------------------------
# Course CRUD
# -------------------------------
@app.route('/courses', methods=['POST'])
def create_course():
    data = request.get_json() or {}
    if not all(k in data for k in ('name', 'code', 'credits')):
        abort(400, description="Missing required fields: name, code, credits")
    course = Course(name=data['name'], code=data['code'], credits=int(data['credits']))
    db.session.add(course)
    db.session.commit()
    return jsonify(course.to_dict()), 201

@app.route('/courses', methods=['GET'])
def list_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses])

@app.route('/courses/<int:cid>', methods=['GET'])
def get_course(cid):
    course = Course.query.get_or_404(cid)
    return jsonify(course.to_dict(include_students=True))

@app.route('/courses/<int:cid>', methods=['PUT'])
def update_course(cid):
    course = Course.query.get_or_404(cid)
    data = request.get_json() or {}
    if 'name' in data:
        course.name = data['name']
    if 'code' in data:
        course.code = data['code']
    if 'credits' in data:
        course.credits = int(data['credits'])
    db.session.commit()
    return jsonify(course.to_dict(include_students=True))

@app.route('/courses/<int:cid>', methods=['DELETE'])
def delete_course(cid):
    course = Course.query.get_or_404(cid)
    db.session.delete(course)
    db.session.commit()
    return '', 204

# -------------------------------
# Enrollments (many-to-many)
# -------------------------------
@app.route('/enroll', methods=['POST'])
def enroll_student():
    data = request.get_json() or {}
    if not all(k in data for k in ('student_id', 'course_id')):
        abort(400, description="Missing required fields: student_id, course_id")
    student = Student.query.get_or_404(int(data['student_id']))
    course = Course.query.get_or_404(int(data['course_id']))
    if course not in student.courses:
        student.courses.append(course)
        db.session.commit()
    return jsonify(student.to_dict(include_courses=True)), 200

@app.route('/unenroll', methods=['POST'])
def unenroll_student():
    data = request.get_json() or {}
    if not all(k in data for k in ('student_id', 'course_id')):
        abort(400, description="Missing required fields: student_id, course_id")
    student = Student.query.get_or_404(int(data['student_id']))
    course = Course.query.get_or_404(int(data['course_id']))
    if course in student.courses:
        student.courses.remove(course)
        db.session.commit()
    return jsonify(student.to_dict(include_courses=True)), 200

# Convenience views
@app.route('/students/<int:sid>/courses', methods=['GET'])
def view_student_courses(sid):
    student = Student.query.get_or_404(sid)
    return jsonify({
        "student": student.to_dict(),
        "courses": [c.to_dict() for c in student.courses]
    })

@app.route('/courses/<int:cid>/students', methods=['GET'])
def view_course_students(cid):
    course = Course.query.get_or_404(cid)
    return jsonify({
        "course": course.to_dict(),
        "students": [s.to_dict() for s in course.students]
    })

if __name__ == '__main__':
    app.run(debug=True)
