import os

from dotenv import load_dotenv
from flask import Flask, render_template
from auth.routes import auth_bp
from teams.routes import teams_bp, get_teams

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(teams_bp, url_prefix="/teams")

@app.route('/')
def index():
    process_team, done_team = get_teams()

    return render_template(
        "main/index.html",
        process_team=process_team,
        done_team=done_team
    )

if __name__ == '__main__':
    app.run(debug=True)