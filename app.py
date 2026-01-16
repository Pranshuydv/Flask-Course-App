from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# 🔐 Secret Key (MANDATORY for session)
app.config["SECRET_KEY"] = "mysecretkey"

# Database Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    discount = db.Column(db.Integer, nullable=False)


# ---------------- ROUTES ----------------


@app.route("/")
def home():
    return render_template("Home.html")


# -------- REGISTER --------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if Student.query.filter_by(email=email).first():
            return "User already exists"

        hashed_password = generate_password_hash(password)
        user = Student(username=username, email=email, password=hashed_password)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("Register.html")


# -------- LOGIN --------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = Student.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("dashboard"))

        return "Invalid email or password"

    return render_template("Login.html")


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))


# -------- DASHBOARD --------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    total_courses = Course.query.count()
    total_students = Student.query.count()

    return render_template(
        "Dashboard.html", total_courses=total_courses, total_students=total_students
    )


# -------- COURSES --------
@app.route("/course")
def course():
    courses = Course.query.all()
    return render_template("Course.html", courses=courses)


@app.route("/course/create", methods=["GET", "POST"])
def create_course():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        course = Course(
            name=request.form["course_name"],
            price=int(request.form["course_price"]),
            duration=int(request.form["course_duration"]),
            discount=int(request.form["course_discount"]),
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for("course"))

    return render_template("Create_Course.html")


@app.route("/course/delete/<int:id>")
def delete_course(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for("course"))


# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
