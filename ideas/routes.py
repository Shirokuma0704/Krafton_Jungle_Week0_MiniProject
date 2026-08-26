from flask import Blueprint, render_template, session, request, redirect
from db import db
from bson import objectid
from datetime import datetime, timezone


idea_bp = Blueprint('ideas', __name__)

def is_member(team_id, user_id):
    check = db.team.find_one({"team_id": team_id, "user_id": user_id})
    if check is None:
        return False
    return True


@idea_bp.route('/ideas/<team_id>')
def idea(team_id):
    user_id = session.get('user_id')
    if user_id is None:
        return "401"

    user_id = objectid.ObjectId(user_id)
    team_id = objectid.ObjectId(team_id)
    member_check = is_member(team_id,user_id)
    if not member_check:
        return "403"

    docs = list(db.ideas.find({"team_id": team_id}))
    return render_template('team/idea.html', ideas=docs, user_id= user_id, team_id=team_id)

@idea_bp.route('/ideas/<team_id>/add', methods=['POST'])
def add_idea(team_id):
    user_id = session.get('user_id')
    if user_id is None:
        return "401"

    user_id = objectid.ObjectId(user_id)
    team_id = objecti_d.ObjectId(team_id)
    member_check = ismember(team_id, user_id)
    if not member_check:
        return "403"

    title = request.form['title']
    content = request.form['content']
    db.ideas.insert_one({"team_id": team_id, "author_id":user_id, "title":title, "content":content, "created_at":datetime.now(timezone.utc)})
    return redirect(url_for('/ideas/{team_id}'))

@idea_bp.route('/ideas/<idea_id>/delete', methods=['POST'])
def del_idea(idea_id):

    user_id = session.get('user_id')
    if user_id is None:
        return "401"
    user_id = objectid.ObjectId(user_id)

    idea_id = objectid.ObjectId(idea_id)
    idea_data = db.ideas.find_one({"_id": idea_id})
    if idea_data is None:
        return "404"

    if user_id != idea_data["author_id"]:
        return "403"

    team_id = idea_data["team_id"]
    member_check = is_member(team_id, user_id)
    if not member_check:
        return "403"


    db.ideas.delete_one({"_id": idea_id})
    return redirect(url_for('/ideas/{team_id}'))

@idea_bp.route('/ideas/<idea_id>/edit', methods=['POST'])
def edit_idea(idea_id):

    user_id = session.get('user_id')
    if user_id is None:
        return "401"
    user_id = objectid.ObjectId(user_id)

    idea_id = objectid.ObjectId(idea_id)
    idea_data = db.ideas.find_one({"_id": idea_id})
    if idea_data is None:
        return "404"

    if user_id != idea_data["author_id"]:
        return "403"

    team_id = idea_data["team_id"]
    member_check = is_member(team_id, user_id)
    if not member_check:
        return "403"
    title = request.form['title']
    content = request.form['content']
    db.ideas.update_one({"_id": idea_id}, {"$set": {"title":title, "content":content}})
    return redirect(url_for('/ideas/{team_id}'))

