from flask import redirect, render_template, request, session, url_for

from controllers.abstract_controller import AbstractController
from models.user import UserSigninDto, UserSignupDto
from models.user_info import UserInfoCreateDto
from services.user_services import UserServices


class UserController(AbstractController):
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
                return redirect(url_for("day_index"))
            except ValueError as e:
                return render_template("signin.html", error=str(e))
        
        return render_template("signin.html")
    
    def signup(self):
        questions = self.user_services.get_user_info_questions()
        if request.method == "POST":
            try:
                info = [
                    UserInfoCreateDto(
                        question_id=question.id, 
                        points=int(request.form.get(f"question_{question.id}"))
                    )
                    for question in questions
                ]
                user_data = UserSignupDto.model_validate({
                    "email": request.form.get("email"),
                    "name": request.form.get("name"),
                    "password": request.form.get("password"),
                    "password2": request.form.get("password2"),
                    "info": info
                })
                user = self.user_services.signup(user_data)
                self._add_user_data_to_session(user.id, user.name)
                return redirect(url_for("day_index"))
            except ValueError as e:
                return render_template("signup.html", questions=questions, error=str(e))
        
        return render_template("signup.html", questions=questions)
