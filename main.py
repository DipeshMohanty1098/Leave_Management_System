from flask import Flask, redirect, render_template, url_for, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "hello12345"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applied.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///applied_permission.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Applied(db.Model):
    __tablename__ = "applied"
    _id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    to_date = db.Column(db.String(100))
    from_date = db.Column(db.String(100))
    days = db.Column(db.Integer)
    status = db.Column(db.String(100))
    def __init__(self, name,email, to_date, from_date, days, status):
        self.name = name
        self.email = email
        self.from_date = from_date
        self.to_date = to_date
        self.days = days
        self.status = status

class Users(db.Model):
    _id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    total_leaves = db.Column(db.Integer)
    remaining_leaves = db.Column(db.Integer)
    def __init__(self, name, email, total_leaves, remaining_leaves):
        self.email = email
        self.name = name
        self.total_leaves =total_leaves
        self.remaining_leaves = remaining_leaves

@app.route('/', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            session["email"] = existing_user.email
            session["name"] = existing_user.name
            return redirect(url_for("dashboard"))
        else:
            flash("No such user, please create an account", "info") 
            return redirect(url_for("login"))
    elif ("name" or "email") in session:
        flash("You are already logged in!", "info")
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/register",  methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["email"]
        existing_user= Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Already registered User, Please Login", "info")
            return redirect(url_for("register"))
        else:
            session["name"] = name
            session["email"] = email
            usr = Users(name, email, 28, 28)
            db.session.add(usr)
            db.session.commit()
            return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    if "name" in session:
        user = session["name"]
        email = session["email"]
        print(user)
        print(email)
        return render_template("dashboard.html", 
        users=user,
        email=email, 
        total=Users.query.filter_by(email=email).first().total_leaves, 
        remaining=Users.query.filter_by(email=email).first().remaining_leaves)
    else:
        if "name" not in session:
            return redirect(url_for("login"))

@app.route("/view")
def view():
    return render_template("view.html", values=Users.query.all())

@app.route("/delete")
def delete():
    db.session.query(Users).delete()
    db.session.commit()
    return "success"

@app.route("/apply_leave", methods = ['POST', 'GET'])
def apply_leave():
    if "email" in session:
        if request.method == 'POST':
            to_date = request.form["to"]
            from_date = request.form["from"]
            days_count = request.form["days"]
            if Users.query.filter_by(email=session["email"]).first().remaining_leaves < int(days_count):
                flash("Sorry! Your Leave application cannot be submitted because you do not have enough paid leaves.", "info")
                return redirect(url_for("dashboard"))
            else:
                application = Applied( 
                session["name"], 
                session["email"],
                to_date, 
                from_date, 
                days_count,
                "Pending")
                db.session.add(application)
                db.session.commit()
                update_user = Users.query.filter_by(email=session["email"]).first()
                update_user.remaining_leaves -= int(days_count) 
                db.session.commit()
                flash("Application Successfully Submitted!", "info")
                return redirect(url_for("dashboard"))
    else:
        flash("Please login to apply for a leave!", "info")
        return redirect(url_for("login"))
    return render_template("apply_leave.html")

@app.route("/view_applications")
def view_applications():
    return render_template("view_applications.html", values=Applied.query.all())

@app.route("/view_applications_user")
def view_applications_user():
    return render_template("view_applications_user.html", 
    name=Applied.query.filter_by(email=session["email"]).first().name,
    email=Applied.query.filter_by(email=session["email"]).first().email,
    id=Applied.query.filter_by(email=session["email"]).first()._id,
    from_date=Applied.query.filter_by(email=session["email"]).first().from_date,
    to_date=Applied.query.filter_by(email=session["email"]).first().to_date,
    days=Applied.query.filter_by(email=session["email"]).first().days,
    status=Applied.query.filter_by(email=session["email"]).first().status,

    )

@app.route("/view_applications_admin")
def view_applications_admin():
    pass


@app.route("/logout")
def logout():
    session.pop("name", None)
    session.pop("email", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)