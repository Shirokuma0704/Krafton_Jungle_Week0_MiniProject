import os

from dotenv import load_dotenv
from flask import Flask, render_template
from auth.routes import auth_bp
from teams.routes import teams_bp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(teams_bp, url_prefix="/teams")

@app.route('/')
def index():
    return render_template("main/index.html")

if __name__ == '__main__':
    app.run(debug=True)