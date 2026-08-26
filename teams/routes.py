from flask import Blueprint, request, g, redirect, url_for, render_template, session, flash
from bson import ObjectId
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
    return redirect(url_for("index"));

@teams_bp.route("/making_team", methods=['POST'])
def making_team():
    if request.method == "POST":
        if g.user is None:
            flash("로그인이 필요합니다.")
            return redirect(url_for("auth.login"))

        teamid = request.form.get("teamid") # 팀명
        title = request.form.get("title") # 목표/주제
        count= request.form.get("peoplenum") # 몇 명인지
        
        if not all([teamid, title, count]):
            flash("모든 항목을 입력해주세요.")
            return redirect(url_for("index"))

        peoplenum = int(count)

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
            "team_name": teamid,
            "title": title,
            "peoplenum": peoplenum,
            "king_id": kingid,
            "status" : TeamStatus.IDEA.value,
            "code": code,
            "members": [kingid],
            "criteria": []
        }

        team_collection.insert_one(team)

    return redirect(url_for("index"))

@teams_bp.route("/join_team", methods=['POST'])
def join_team():
        if g.user is None:
            flash("로그인이 필요합니다.")
            return redirect(url_for("auth.login"))
        
        code = request.form.get("code") #초대 코드

        if not code:
            flash("존재하지 않는 초대 코드입니다.")
            return redirect(url_for("index"))

        team = team_collection.find_one({"code": code})

        # 팀이 없을 때
        if team is None:
            flash("존재하지 않는 초대 코드입니다.")
            return redirect(url_for("index"))
        
        if len(team["members"]) >= team["peoplenum"]: 
            flash("정원을 초과하였습니다.")
            return redirect(url_for("index"))
        
        team_collection.update_one(
            {"_id": team["_id"]},
            {
                "$addToSet": { # addToSet: 배열에 이미 존재하지 않는 값을 추가
                    "members": g.user["_id"]
                }
            }
        )

        return redirect(url_for("index"))

def get_teams():
    if g.user is None:
        return [], []
    teams = list(team_collection.find({"members": g.user["_id"]}))

    process_team = []
    done_team = []

    # 전체 팀 배열에서 진행중인 팀과 종료된 팀을 따로 구분한다.
    for team in teams:
        if team["status"] == TeamStatus.DONE.value:
            done_team.append(team)
        else:
            process_team.append(team)

    return process_team, done_team

@teams_bp.route("/<team_id>")
def get_team(team_id):
    if g.user is None:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))
    
    team = team_collection.find_one({"_id": ObjectId(team_id)})

    if team is None:
        flash("존재하지 않는 팀입니다.")
        return redirect(url_for("index"))
    #내 팀이 아닌 경우 메인화면으로 이동
    if g.user["_id"] not in team["members"]:
        flash("접근 권한이 없는 팀입니다.")
        return redirect(url_for("index"))
    
    return render_template("team/votes.html", team=team)