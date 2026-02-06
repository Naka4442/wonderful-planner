import os

from flask import Flask, g, jsonify, render_template, request, redirect, session
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from models import *
from repositories import *
from services import *
from controllers import *
from routers import *
from utils.date_utils import get_datetime_from_day_and_time


load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.static_folder = 'static'

app.config['SESSION_COOKIE_DOMAIN'] = None  # None - для всех доменов
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # True если HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True

class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Определяем протокол
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        
        # Определяем хост
        host = environ.get('HTTP_X_FORWARDED_HOST')
        if host:
            environ['HTTP_HOST'] = host
            
        return self.app(environ, start_response)

app.wsgi_app = ReverseProxied(app.wsgi_app)
Base.metadata.create_all(engine)

@app.before_request
def before_request_db():
    # Создаем сессию для текущего запроса и сохраняем ее в g
    g.db = SessionLocal()


@app.teardown_appcontext
def teardown_request_db(exception=None):
    db: Session = g.pop('db', None)
    if db is not None:
        db.close()

# Репозитории
user_repository = UserRepository()

# Сервисы
user_services = UserServices(user_repository)
# task_services = TaskServices()

# Контроллеры
user_controller = UserController(user_services)
# task_controller = TaskController(task_services)

# Роутеры
user_router = UserRouter(app, "users", user_controller)
# task_router = TaskRouter(app, "task", task_controller)


# @app.route("/")
# def index():
#     if "user_id" not in session:
#         return redirect("/signin")

#     if request.args.get("date") is not None:
#         d = request.args.get("date").split("-")
#         day = date(
#             int(d[0]),
#             int(d[1]),
#             int(d[2])
#         )
#     else:
#         day = date.today()

#     user_name = session["user_name"]
    
#     # Создаем новую сессию для этого запроса
#     with get_db() as db:
#         task_services = TaskServices(db)
        
#         pos_count, pos_difference = task_services.get_positive_difference_by_day(session["user_id"], day)
#         neg_count, neg_difference  = task_services.get_negative_difference_by_day(session["user_id"], day)
#         difficulty = task_services.get_difficulty_by_day(session["user_id"], day)

#         schedule = task_services.get_schedule(session["user_id"], day)
#         no_repeated_tasks = task_services.get_not_event_tasks_by_day(session["user_id"], day)
        
#         undone = [task for task in no_repeated_tasks if not task.is_done]
#         done = [task for task in no_repeated_tasks if task.is_done]
#         return render_template(
#             "index.html", 
#             user_name=user_name, 
#             undone=undone,
#             done=done,
#             schedule=schedule,
#             count_done=len(done),
#             count_undone=len(undone),
#             pos_count=pos_count,
#             pos_difference=pos_difference,
#             neg_difference=neg_difference,
#             neg_count=neg_count,
#             difficulty=difficulty
#         )

# @app.route("/weekly")
# def weekly():
#     if "user_id" not in session:
#         return redirect("/signin")
    
#     if request.args.get("date") is not None:
#         d = request.args.get("date").split("-")
#         day = date(
#             int(d[0]),
#             int(d[1]),
#             int(d[2])
#         )
#     else:
#         day = date.today()
    
#     user_name = session["user_name"]
    
#     with get_db() as db:
#         task_services = TaskServices(db)

#         pos_count, pos_difference = task_services.get_positive_difference_by_week(session["user_id"], day)
#         neg_count, neg_difference = task_services.get_negative_difference_by_week(session["user_id"], day)
#         difficulty = task_services.get_difficulty_by_week(session["user_id"], day)
#         schedule = task_services.get_week_schedule(session["user_id"])
#         #no_repeated_tasks = task_services.get_not_repeated_tasks(session["user_id"])
        
#         #undone = [task for task in no_repeated_tasks if not task.is_done]
#         #done = [task for task in no_repeated_tasks if task.is_done]
        
#         return render_template(
#             "weekly.html",
#             user_name=user_name,
#             #undone=undone,
#             #done=done,
#             schedule=schedule,
#             #count_done=len(done),
#             #count_undone=len(undone),
#             difficulty=difficulty,
#             pos_difference=pos_difference,
#             pos_count=pos_count,
#             neg_difference=neg_difference,
#             neg_count=neg_count
#         )

# @app.route("/create", methods = ["GET", "POST"])
# def create():
#     if "user_id" not in session:
#         return redirect("/signin")
    
#     user_name = session["user_name"]
    
#     if request.method == "POST":
#         title = request.form.get("title")
#         description = request.form.get("description")
#         difficulty = request.form.get("difficulty")
        
#         supposed_hours = request.form.get("time-hours") if request.form.get("time-hours") else 0
#         supposed_minutes = request.form.get("time-minutes") if request.form.get("time-minutes") else 0
#         supposed_time = int(supposed_hours) * 60 + int(supposed_minutes)
        
#         is_event = bool(int(request.form.get("event")))
#         is_repeated = bool(request.form.get("is_repeated"))
#         repeat_time_start = request.form.get("repeat_time_start")
#         repeat_time_end = request.form.get("repeat_time_end")
#         repeat_weekday = int(request.form.get("repeat_weekday"))
        
#         if is_event:
#             start_time = request.form.get("start-time")
#             end_time = request.form.get("end-time")
#         else:
#             start_time_day = request.form.get("start-time-day")
#             start_time_time = request.form.get("start-time-time")
#             start_time = get_datetime_from_day_and_time(start_time_day, start_time_time) if len(start_time_time) > 0 else start_time_day 
#             end_time = ""

#         with get_db() as db:
#             task_services = TaskServices(db)
#             try:
#                 task_services.create(
#                     title, 
#                     session["user_id"], 
#                     description, 
#                     difficulty, 
#                     supposed_time,
#                     is_event,
#                     is_repeated,
#                     repeat_time_start if len(repeat_time_start) > 0 else None,
#                     repeat_time_end if len(repeat_time_end) > 0 else None,
#                     repeat_weekday,
#                     start_time,
#                     end_time if len(end_time) > 0 else None
#                 )
#                 return redirect("/")
#             except ValueError as e:
#                 return render_template("create.html", error=str(e), user_name=user_name)
    
#     return render_template("create.html", user_name=user_name)

# @app.route("/profile")
# def profile():
#     if "user_id" in session:
#         user_name = session["user_name"]
#     else:
#         return redirect("/signin")
    
#     return render_template("profile.html", user_name=user_name)

# @app.route("/check", methods=["POST"])
# def check():
#     body = request.get_json()
#     task_id = body.get("taskId")
#     minutes = body.get("minutes")
    
#     with get_db() as db:
#         task_services = TaskServices(db)
#         try:
#             task_services.check_task(int(task_id), int(minutes), session["user_id"])
#             return jsonify({"success": True})
#         except ValueError as e:
#             return jsonify({"error": str(e)}), 400

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect("/signin")

if __name__ == "__main__":
    debug = os.getenv("FLASK_ENV", "production") == "development"
    app.run(host="0.0.0.0", port=5000, debug=debug)