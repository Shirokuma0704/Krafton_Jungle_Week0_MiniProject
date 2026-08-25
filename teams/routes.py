from flask import Blueprint, render_template

teams_bp = Blueprint('teams', __name__)

@teams_bp.route
def teams():
    return "teams page"
