from flask import Flask, render_template, request, redirect, session
from models import get_db, engine, Base, User
from services import UserServices
from dotenv import load_dotenv
import os


Base.metadata.create_all(engine)
load_dotenv()
with get_db() as db:
    user_services = UserServices(db)

    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.static_folder = 'static'

    @app.route("/")
    def index():
        if "user_id" in session:
            user_name = session["user_name"]
        else:
            user_name = "Не вошел"
        ip_address = request.remote_addr
        return render_template("index.html", ip_address=ip_address, user_name=user_name)



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

    @app.route("/signin", methods = ["GET", "POST"])
    def signin():
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            try:
                user_services.signin( email, password)
                return redirect("/")
            except ValueError as e:
                return render_template("signin.html", error=str(e))
        elif request.method == "GET":
            return render_template("signin.html")


    app.run(debug=True)