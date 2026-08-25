from flask import Blueprint

vote_bp = Blueprint('vote', __name__)

@vote_bp.route
def vote():
    return "vote page"
