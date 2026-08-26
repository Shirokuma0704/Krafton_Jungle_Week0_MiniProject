from flask import Blueprint, render_template, redirect, session, request, url_for, g, flash
from bson import ObjectId #MongoDB의 ID를 object로 내려주지만 파이썬에는 ObjectId라는 클래스가 내장되어있지 않아, 별도로 import해주어 사용
from werkzeug.security import generate_password_hash, check_password_hash

from db import db

auth_bp = Blueprint('auth', __name__)
users = db["users"]

@auth_bp.before_app_request
def load_nickname():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = users.find_one({
            "_id": ObjectId(user_id)
        })

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":        
        userid = request.form.get("userid")
        password = request.form.get("password")

        if not all([userid, password]):
            flash("아이디와 비밀번호를 입력해주세요.")
            return redirect(url_for("auth.login"))
        #유저 정보 가져오기
        user = users.find_one({"userid": userid})

        if user is None or not check_password_hash(user["password"], password):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.")
            return redirect(url_for("auth.login"))

        session.clear() # 기존에 세션이 있을수도 있으니 지우기
        session["user_id"] = str(user["_id"]) # 세션에 사용자 등록

        return redirect(url_for("index")) # 로그인 성공 시, 메인화면으로 이동
    
    return render_template("auth/login.html") # GET의 경우, 페이지만 보여줌

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        userid = request.form.get("userid")
        nickname = request.form.get("nickname")
        password = request.form.get("password")
        repassword = request.form.get("repassword")

        # 모두 입력 안 했을 경우
        if not all([userid, nickname, password, repassword]):
            flash("모든 항목을 입력해 주세요.")
            returnredirect(url_for("auth.signup"))
        if users.find_one({"userid": userid}):
            flash("이미 사용중인 아이디입니다.")
            return redirect(url_for("auth.signup"))
        
        #비밀번호가 일치하지 않는 경우
        if (password != repassword):
            flash("비밀번호가 일치하지 않습니다.")
            return redirect(url_for("auth.signup"))
        if (len(password) < 8):
            flash("비밀번호는 8자 이상이여야 합니다.")
            return redirect(url_for("auth.signup"))
        
        password_hash = generate_password_hash(password)

        user = {
            "userid": userid,
            "nickname": nickname,
            "password": password_hash
        }

        users.insert_one(user)

        return redirect(url_for("auth.login"))
    
    return render_template("auth/signup.html")

@auth_bp.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index")) #로그아웃 성공 시, 메인화면으로 이동