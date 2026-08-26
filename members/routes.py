from flask import Blueprint, render_template, g, flash, redirect, url_for
from bson import ObjectId
from db import db
member_bp = Blueprint("members", __name__)
team_collection = db["teams"]
user_collection = db["users"]

@member_bp.route("/<team_id>")
def members(team_id):
    if g.user is None:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))
    
    team = team_collection.find_one({"_id": ObjectId(team_id)}) # 팀 id에 맞는 팀 정보들 찾기

    #팀이 존재하지 않을 경우 메인화면으로 이동
    if team is None:
        flash("존재하지 않는 팀입니다.")
        return redirect(url_for("index"))

    if g.user["_id"] not in team["members"]:
        flash("접근 불가능합니다.")
        return redirect(url_for("index"))


    # 팀원 id, 팀원 닉네임 매칭하는게 필요
    # 딕셔너리 형태로 저장
    matching_data = {}

    for member in team["members"]:
        user = user_collection.find_one({"_id": member})
        matching_data[member] = user["nickname"]

    return render_template("team/members.html", members=matching_data, team=team)

@member_bp.route("/<team_id>/<member_id>/kick", methods=["POST"])
def kick(team_id, member_id):
    if g.user is None:
        flash("로그인이 필요합니다.")
        return redirect(url_for("auth.login"))

    team = team_collection.find_one({"_id": ObjectId(team_id)}) # 팀 id에 맞는 팀 정보들 찾기

    #팀이 존재하지 않을 경우 메인화면으로 이동
    if team is None:
        flash("존재하지 않는 팀입니다.")
        return redirect(url_for("index"))

    if team["king_id"] == g.user["_id"]:
        team_collection.update_one(
            {"_id": team["_id"]},
            {
                "$pull": { # pull: 배열에 조건을 만족하는 특정한 요소를 제거
                    "members": ObjectId(member_id)
                }
            }
        )

    return redirect(url_for("members.members", team_id=team_id))