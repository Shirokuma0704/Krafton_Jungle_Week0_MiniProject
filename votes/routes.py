from flask import Blueprint, request, render_template, session, redirect, url_for
from db import db
from bson import objectid
from datetime import datetime
from teams.routes import TeamStatus

vote_bp = Blueprint('votes', __name__)


def is_member(team_id, user_id):
    check = db.teams.find_one({"_id": team_id, "members": user_id})
    if check is None:
        return False
    return True

def not_available_connection():
    return "잘못된 접근입니다", 403

def is_leader(team_id, user_id):
    check = db.teams.find_one({"_id": team_id,"king_id": user_id,  "members": user_id})
    if check is None:
        return False
    return True

@vote_bp.route('/<team_id>') #Vote 페이지 진입
def vote(team_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401

    user_id = objectid.ObjectId(user_id)
    team_id= objectid.ObjectId(team_id)
    if not is_member(team_id, user_id):
        return "잘못된 접근입니다.", 403

    teams_data = db.teams.find_one({"_id": team_id})
    leader_check = is_leader(team_id, user_id)

    ideas = list(db.ideas.find({"team_id": team_id}))

    if teams_data['status'] == TeamStatus.IDEA:
        return render_template('team/votes.html', user=user_id, leader=leader_check, status=0, team_id = team_id, team=teams_data)
    elif teams_data['status'] == TeamStatus.VOTING:
        vote_chk = vote_check(team_id)
        return render_template('team/votes.html', user=user_id, leader=leader_check, status=1, vote_check=vote_chk, team_id = team_id, ideas= ideas, criteria=teams_data['criteria'], team=teams_data)
    elif teams_data['status'] == TeamStatus.DONE:
        return redirect(url_for("votes.vote_result", team_id=team_id))
    else:
        return "알 수 없는 팀 상태입니다.", 500

def vote_check(team_id):
    user_id = session.get("user_id")
    user_id = objectid.ObjectId(user_id)
    if not is_member(team_id, user_id):
        return False

    if db.votes.find_one({"team_id": team_id, "voter_id": user_id}) is None:
        return False
    return True


@vote_bp.route('/<team_id>/start', methods=['POST']) #투표시작
def start_vote(team_id):

    team_id = objectid.ObjectId(team_id)
    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)

    member_check = is_member(team_id, user_id)
    leader_check = is_leader(team_id, user_id)
    if not leader_check or not member_check:
        return "잘못된 접근입니다.", 403

    teams_data = db.teams.find_one({"_id": team_id})

    status = teams_data['status']
    if status != TeamStatus.IDEA:
        if status == TeamStatus.VOTING:
            return "이미 투표중입니다.", 409
        if status == TeamStatus.DONE:
            return "투표 종료된 방입니다.", 409
        else:
            return "알 수 없는 팀 상태입니다.", 500

    criteria = request.form.getlist("criteria")

    criteria = [criteria.strip() for criteria in criteria]
    criteria = [criteria for criteria in criteria if criteria != ""]

    if len(criteria) == 0 or len(criteria) > 5:
        return "잘못된 접근입니다", 400

    db.teams.update_one({"_id": team_id}, {"$set": {"status": TeamStatus.VOTING.value, "criteria": criteria}})
    return redirect(url_for("votes.vote", team_id=team_id))

@vote_bp.route('/<team_id>', methods=['POST']) #개별 투표
def vote_individual(team_id):
    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)
    team_id = objectid.ObjectId(team_id)
    if not is_member(team_id, user_id):
        return "잘못된 접근입니다", 403

    teams_data = db.teams.find_one({"_id": team_id})
    if teams_data is None:
        return "존재하지 않는 팀입니다.", 404

    status = teams_data['status']
    if status != TeamStatus.VOTING:
        if status == TeamStatus.IDEA:
            return "투표 진행 전입니다.", 409
        if status == TeamStatus.DONE:
            return "투표 종료된 방입니다.", 409
        else:
            return "알 수 없는 팀 상태입니다.", 500


    vote_data = db.votes.find_one({"team_id": team_id, "voter_id": user_id})
    if vote_data is not None:
        return "이미 완료한 투표입니다.", 409


    idea_list = list(db.ideas.find({"team_id": team_id}))
    if not idea_list:
        return "등록된 아이디어가 없습니다.", 409
    criteria_list = teams_data["criteria"]

    score = []
    for idea in idea_list:
        for i, name in enumerate(criteria_list):
            key = f"score_{idea['_id']}_{i}"
            raw = request.form.get(key)
            if raw is None:
                # return "전부 투표되지 않았습니다.", 400
                return key
            if raw not in ["1", "2", "3", "4", "5"]:
                return "잘못된 접근입니다", 403
            raw = int(raw)

            score.append({"idea_id": idea["_id"], "criterion": name, "score": raw})
    db.votes.insert_one({"team_id": team_id, "voter_id": user_id, "score": score, "created_at": datetime.now()})

    members = teams_data["members"]
    total = len(members)
    voted = db.votes.count_documents({"team_id": team_id})

    if voted >= total:
        db.teams.update_one({"_id": team_id}, {"$set": {"status": TeamStatus.DONE.value}})
    return redirect(url_for("votes.vote", team_id=team_id))




@vote_bp.route('/<team_id>/result', methods=['GET']) #투표 결과
def vote_result(team_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)
    team_id = objectid.ObjectId(team_id)
    if is_member(team_id, user_id) is False:
        return not_available_connection()

    teams_data = db.teams.find_one({"_id": team_id})
    if teams_data is None:
        return "존재하지 않는 팀입니다.", 404

    status = teams_data['status']
    if status != TeamStatus.DONE:
        if status == TeamStatus.IDEA:
            return "투표 진행 전입니다.", 409
        if status == TeamStatus.VOTING:
            return "투표 중인 방입니다.", 409
        else:
            return "알 수 없는 팀 상태입니다.", 500

    members = teams_data["members"]

    vote_data = list(db.votes.find({"team_id": team_id}))
    if not vote_data:
        return "집계할 투표 기록이 없습니다.", 409

    score_sum = {}
    score_count = {}

    for vote_total in vote_data:
        for s in vote_total['score']:
            key = (s['idea_id'], s['criterion'])
            score_sum[key] = score_sum.get(key, 0) + s['score']
            score_count[key] = score_count.get(key, 0) + 1

    ave_score = []

    criteria_list = teams_data["criteria"]
    idea_list = list(db.ideas.find({"team_id": team_id}))

    for idea in idea_list:
        criteria = {}
        for name in criteria_list:
            key = (idea['_id'], name)
            criteria[name] = score_sum.get(key, 0) / score_count.get(key, 1)
        ave_score.append({
            "title": idea['title'],
            "score": criteria,
            "total": sum(criteria.values()) / len(criteria),
        })

    ave_score = sorted(ave_score, key=lambda x: x['total'], reverse=True)

    return render_template('team/votes.html', team_id=team_id, ave_score=ave_score, status=2, team=teams_data)



@vote_bp.route('/<team_id>/forcestop', methods=['POST']) #방장 정지
def force_stop(team_id):
    team_id = objectid.ObjectId(team_id)
    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)

    member_check = is_member(team_id, user_id)
    leader_check = is_leader(team_id, user_id)
    if not leader_check or not member_check:
        return "잘못된 접근입니다.", 403

    if db.teams.find_one({"_id": team_id, "status": TeamStatus.DONE}) is not None:
        return "잘못된 접근입니다.", 403

    db.teams.update_one({"_id": team_id}, {"$set": {"status": TeamStatus.DONE.value}})

    teams_data = db.teams.find_one({"_id": team_id})
    return redirect(url_for("votes.vote", team_id=team_id))
