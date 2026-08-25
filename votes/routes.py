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

@vote_bp.route('/vote/<team_id>') #Vote 페이지 진입
def vote(team_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "403"

    user_id = objectid.ObjectId(user_id)
    team_id= objectid.ObjectId(team_id)
    if not is_member(team_id, user_id):
        return "403"

    teams_data = db.teams.find({"_id": team_id})

    if teams_data['status'] == 0:
        render_template()
    elif teams_data['status'] == 1:
        vote_count(team_id)
        render_template()
    elif teams_data['status'] == 2:
        vote_result(team_id)
        render_template()
    else:
        return "401"

def vote_count(team_id):

def vote_result(team_id):
