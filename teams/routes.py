from flask import Blueprint, request, g, redirect, url_for, render_template
from enum import Enum
import string, random
from db import db

teams_bp = Blueprint('teams', __name__)
team_collection = db["teams"]

class TeamStatus(str, Enum):
    IDEA = "IDEA"
    VOTING = "VOTING"
    DONE = "DONE"

@teams_bp.route("/")
def teams():
    return render_template("main/index.html");

@teams_bp.route("/making_team", methods=['POST'])
def making_team():
    if request.method == "POST":
        teamid = request.form.get("teamid") # 팀명
        title = request.form.get("title") # 목표/주제
        peoplenum= int(request.form.get("peoplenum")) # 몇 명인지

        kingid = g.user["_id"] #방장 id 

        while True:
            _LENGTH = 6
            string_pool = string.ascii_letters + string.digits
            code = ""

            for _ in range(_LENGTH):
                code += random.choice(string_pool)
            if not team_collection.find_one({"code": code}):
                break

        team = {
            "teamid": teamid,
            "title": title,
            "peoplenum": peoplenum,
            "kingid": kingid,
            "status" : TeamStatus.IDEA.value,
            "code": code,
            "members": [kingid],
        }

        team_collection.insert_one(team)

        return redirect(url_for("index"))
    return render_template("main/index.html");

@teams_bp.route("/join_team", methods=['POST'])
def join_team():
        code = request.form.get("code") #초대 코드

        team = team_collection.find_one({"code": code})

        # 팀이 없을 때
        if team is None:
            return "존재하지 않는 초대 코드입니다."

        if len(team["members"]) >= team["peoplenum"]:
            return "인원이 가득 찼습니다."

        team_collection.update_one(
            {"_id": team["_id"]},
            {
                "$addToSet": { # addToSet: 배열에 이미 존재하지 않는 값을 추가
                    "members": g.user["_id"]
                }
            }
        )

        return redirect(url_for("index"))