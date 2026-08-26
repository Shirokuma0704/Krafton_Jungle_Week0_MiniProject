from flask import Blueprint, render_template, session, request, redirect, url_for
from db import db
from bson import objectid
from datetime import datetime, timezone



idea_bp = Blueprint('ideas', __name__)

def is_member(team_id, user_id):
    check = db.teams.find_one({"_id": team_id, "members": user_id})
    if check is None:
        return False
    return True


@idea_bp.route('/<team_id>')
def idea(team_id):
    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401

    user_id = objectid.ObjectId(user_id)
    team_id = objectid.ObjectId(team_id)
    member_check = is_member(team_id,user_id)
    if member_check is False:
        return "잘못된 접근입니다.", 403

    docs = list(db.ideas.find({"team_id": team_id}))
    return render_template('team/_ideas.html', ideas=docs, user= user_id, team=team_id)

@idea_bp.route('/<team_id>/add', methods=['POST'])
def add_idea(team_id):
    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401

    user_id = objectid.ObjectId(user_id)
    team_id = objectid.ObjectId(team_id)
    member_check = is_member(team_id, user_id)
    if member_check is False:
        return "잘못된 접근입니다.", 403
    team_data = db.teams.find_one({"_id": team_id, "members": user_id})

    title = request.form['title']
    content = request.form['content']
    db.ideas.insert_one({"team_id": team_id, "author_id":user_id, "title":title, "content":content, "created_at":datetime.now(timezone.utc)})
    return redirect(url_for('ideas.idea', team_id=team_data["_id"]))

@idea_bp.route('/<idea_id>/delete', methods=['POST'])
def del_idea(idea_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)

    idea_id = objectid.ObjectId(idea_id)
    idea_data = db.ideas.find_one({"_id": idea_id})
    if idea_data is None:
        return "존재하지 않는 아이디어입니다.", 404

    if user_id != idea_data["author_id"]:
        return "작성자만 삭제할 수 있습니다.", 403

    team_id = idea_data["team_id"]
    member_check = is_member(team_id, user_id)
    if not member_check:
        return "잘못된 접근입니다.", 403


    db.ideas.delete_one({"_id": idea_id})
    return redirect(url_for('ideas.idea', team_id=idea_data["team_id"]))

@idea_bp.route('/<idea_id>/edit', methods=['POST'])
def edit_idea(idea_id):

    user_id = session.get("user_id")
    if user_id is None:
        return "로그인이 필요합니다.", 401
    user_id = objectid.ObjectId(user_id)

    idea_id = objectid.ObjectId(idea_id)
    idea_data = db.ideas.find_one({"_id": idea_id})
    if idea_data is None:
        return "존재하지 않는 아이디어입니다.", 404

    if user_id != idea_data["author_id"]:
        return "작성자만 수정할 수 있습니다.", 403

    team_id = idea_data["team_id"]
    member_check = is_member(team_id, user_id)
    if not member_check:
        return "잘못된 접근입니다.", 403
    title = request.form['title']
    content = request.form['content']
    db.ideas.update_one({"_id": idea_id}, {"$set": {"title":title, "content":content}})
    return redirect(url_for('ideas.idea', team_id=idea_data["team_id"]))

