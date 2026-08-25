from flask import Blueprint, render_template, redirect, request, url_for
from werkzeug.security import generate_password_hash

from db import db

auth_bp = Blueprint('auth', __name__)
users = db["users"]

@auth_bp.route('/login')
def login():
    return render_template("auth/login.html")

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        userid = request.form.get("userid")
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        # 모두 입력 안 했을 경우
        if not all([userid, nickname, password, repassword]):
            return render_template(
                "auth/signup.html",
                error="모든 항목을 입력해 주세요.")
        if users.find_one({"userid": userid}):
            return render_template(
                "auth/signup.html",
                error="이미 사용중인 아이디입니다.")
        
        #비밀번호가 일치하지 않는 경우
        if (password != repassword):
            return render_template(
                "auth/signup.html",
                error="비밀번호가 일치하지 않습니다.")
        if (len(password) < 8):
            return render_template(
                "auth/signup.html",
                error="비밀번호는 8자 이상이여야 합니다."
            )
        password_hash = generate_password_hash(password)

        user = {
            "userid": userid,
            "nickname": nickname,
            "password": password_hash
        }

        users.insert_one(user)

        return redirect(url_for("auth.login"))
    
    return render_template("auth/signup.html")