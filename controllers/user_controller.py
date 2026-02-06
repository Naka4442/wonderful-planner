from datetime import date
from flask import redirect, render_template, request, session
from models.base import get_db
from services.user_services import UserServices


class UserController:
    def __init__(self, user_services: UserServices):
        self.user_services = user_services

    def signin(self):
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            
            with get_db() as db:
                user_services = UserServices(db)
                try:
                    user = user_services.signin(email, password)
                    session.update({"user_id": user.id})
                    session.update({"user_name": user.name})
                    return redirect("/")
                except ValueError as e:
                    return render_template("signin.html", error=str(e))
        
        return render_template("signin.html")
    
    def signup():
        if request.method == "POST":
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            password2 = request.form.get("password2")
            
            with get_db() as db:
                user_services = UserServices(db)
                try:
                    user = user_services.signup(name, email, password, password2)
                    # Сохраняем в сессии
                    session["user_id"] = user.id
                    session["user_name"] = user.name
                    return redirect("/")
                except ValueError as e:
                    return render_template("signup.html", error=str(e))
        
        return render_template("signup.html")
