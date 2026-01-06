from flask import Flask, render_template, request, redirect
from models import get_db, engine, Base, User
from services import UserServices


Base.metadata.create_all(engine)
with get_db() as db:
    user_services = UserServices(db)

    app = Flask(__name__)
    app.static_folder = 'static'

    @app.route("/")
    def index():
        ip_address = request.remote_addr
        return render_template("index.html", ip_address=ip_address)


    @app.route("/signup", methods = ["GET", "POST"])
    def signup():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            try:
                user_services.signup(name, email, password, password2)
                return redirect("/")
            except ValueError as e:
                return render_template("signup.html", error=str(e))
        elif request.method == "GET":
            return render_template("signup.html")

    @app.route("/signin")
    def signin():
        return render_template("signin.html")


    app.run(debug=True)