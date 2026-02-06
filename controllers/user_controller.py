from flask import redirect, render_template, request, session

from models.user import UserSigninDto, UserSignupDto
from services.user_services import UserServices


class UserController:
    def __init__(self, user_services: UserServices):
        self.user_services = user_services

    def _add_user_data_to_session(self, user_id: int, user_name: str):
        session.update({"user_id": user_id})
        session.update({"user_name": user_name})

    def signin(self):
        if request.method == "POST":
            try:
                user_data = UserSigninDto(**request.form)
                user = self.user_services.signin(user_data)
                self._add_user_data_to_session(user.id, user.name)
                return redirect("/")
            except ValueError as e:
                return render_template("signin.html", error=str(e))
        
        return render_template("signin.html")
    
    def signup(self):
        if request.method == "POST":
            try:
                user_data = UserSignupDto(**request.form)
                user = self.user_services.signup(user_data)
                self._add_user_data_to_session(user.id, user.name)
                return redirect("/")
            except ValueError as e:
                return render_template("signup.html", error=str(e))
        
        return render_template("signup.html")
