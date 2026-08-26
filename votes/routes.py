from flask import Blueprint, request, render_template, session
from db import db
from bson import objectid

vote_bp = Blueprint('vote', __name__)


def is_member(team_id, user_id):
    check = db.team_members.find_one({"team_id": team_id, "user_id": user_id})
    if check is None:
        return False
    return True

def is_leader(team_id, user_id):
    check = db.team.find_one({"team_id": team_id,"team_leader_id": user_id,  "user_id": user_id})
    if check is None:
        return False
    return True

@vote_bp.route('/votes/<team_id>') #Vote 페이지 진입
def vote(team_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "402"

    user_id = objectid.ObjectId(user_id)
    team_id= objectid.ObjectId(team_id)
    if not is_member(team_id, user_id):
        return "403"

    teams_data = db.teams.find({"_id": team_id})
    is_leader = is_leader(team_id, user_id)

    if teams_data['status'] == IDEA:
        render_template('team/_vote.html', user=user_id, leader=is_leader, status=0)
    elif teams_data['status'] == VOTING:
        vote_check = vote_check(team_id)
        render_template('team/_vote.html', user=user_id, leader=is_leader, status=1, vote_check=vote_check)
    elif teams_data['status'] == DONE:
        vote_result = vote_result(team_id)
        return redirect(url_for("teamteam_result", team_id=team_id)) #vote/result으로 리다이렉트
    else:
        return "401"

def vote_check(team_id):
db.votes.find({"team_id": team_id})



def vote_result(team_id):
# 업로드 투표 통계생성


@vote_bp.route('/votes/<team_id>/start', method=['POST']) #투표시작
def start_vote(team_id,):




@vote_bp.route('/votes/<team_id>', method=['POST']) #개별 투표

@vote_bp.route('/votes/<team_id>/result', method=['GET']) #투표 결과
def
