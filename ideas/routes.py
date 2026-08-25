from flask import Blueprint, render_template

idea_bp = Blueprint('idea', __name__)

@idea_bp.route
def idea():
    return "idea page"
