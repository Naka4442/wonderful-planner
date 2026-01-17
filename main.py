from flask import Flask, jsonify, render_template, request, redirect, session
from models import get_db, engine, Base, User
from services import UserServices, TaskServices
from dotenv import load_dotenv
import os


Base.metadata.create_all(engine)
load_dotenv()
with get_db() as db:
    user_services = UserServices(db)
    task_services = TaskServices(db)

    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    app.static_folder = 'static'

    @app.route("/")
    def index():
        if "user_id" in session:
            user_name = session["user_name"]
            tasks = task_services.get_all(session["user_id"])
            difference = task_services.get_difference(session["user_id"])
        else:
            user_name = "Не вошел"
            tasks = []
            difference = 0
        undone = [task for task in tasks if not task.is_done]
        done = [task for task in tasks if task.is_done]
        return render_template(
            "index.html", 
            user_name=user_name, 
            undone=undone,
            done=done,
            difference=difference
        )



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


    @app.route("/create", methods = ["GET", "POST"])
    def create():
        if "user_id" not in session:
            return redirect("/signin")
        
        user_name = session["user_name"]
        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            difficulty = request.form.get("difficulty")
            
            supposed_hours = request.form.get("time-hours")
            supposed_minutes = request.form.get("time-minutes")
            
            supposed_time = int(supposed_hours) * 60 + int(supposed_minutes)
            
            start_time = request.form.get("start-time")
            end_time = request.form.get("end-time")
            
            is_repeated = bool(request.form.get("is_repeated"))
            repeat_time_start = request.form.get("repeat_time_start")
            repeat_time_end = request.form.get("repeat_time_end")
            repeat_weekday = int(request.form.get("repeat_weekday"))
            
            try:
                task_services.create(
                    title, 
                    session["user_id"], 
                    description, 
                    difficulty, 
                    supposed_time,
                    is_repeated,
                    repeat_time_start if len(repeat_time_start) > 0 else None,
                    repeat_time_end if len(repeat_time_end) > 0 else None,
                    repeat_weekday,
                    start_time if len(start_time) > 0 else None,
                    end_time if len(end_time) > 0 else None
                )
                return redirect("/")
            except ValueError as e:
                return render_template("create.html", error=str(e), user_name=user_name)
        elif request.method == "GET":
            return render_template("create.html", user_name=user_name)
        


    @app.route("/profile")
    def profile():
        if "user_id" in session:
            user_name = session["user_name"]
        else:
            return redirect("/signin")
        return render_template(
            "profile.html", 
            user_name=user_name, 
        )

    @app.route("/check", methods=["POST"])
    def check():
        body = request.get_json()
        task_id = body.get("taskId")
        minutes = body.get("minutes")
        try:
            task_services.check_task(int(task_id), int(minutes), session["user_id"])
            return redirect("/")
        except ValueError as e:
            return jsonify({"error": str(e)})

    app.run(debug=True)