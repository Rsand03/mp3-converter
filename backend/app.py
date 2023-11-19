"""Main application file"""
from flask import Flask, request
from flask_cors import CORS
from backend.youtube import youtube_download, youtube_serve
from backend.user import create_user, login_user, get_user_data

app = Flask(__name__)
CORS(app)


@app.route("/api/signup", methods=["POST"])
def signup():
    """
    User signup route. Creates a new user in the database.
    """
    email = request.get_json().get("email")
    password = request.get_json().get("password")
    password_confirmation = request.get_json().get("password_confirm")

    return create_user(email, password, password_confirmation)


@app.route("/api/login", methods=["POST"])
def login():
    """
    Login route. Checks if the user exists and if the password is correct.

    returns JWT token if the user exists and the password is correct.
    """
    email = request.get_json().get("email")
    password = request.get_json().get("password")

    return login_user(email, password)


@app.route("/api/user_data", methods=["GET"])
def user_data():
    """
    User data route. Returns the user data if the token is valid.
    """
    token = request.headers.get("Authorization")

    return get_user_data(token)


@app.route("/api/download", methods=["POST"])
def download():
    """
    Download content, given a url using yt-dlp.

    Returns a 200 status code and the file name.
    """
    url = request.get_json().get("url")
    platfrom = request.get_json().get("platform")
    media_format = request.get_json().get("format")

    if platfrom == "youtube":
        result = youtube_download(url, media_format)
        return result

    return {"error": "Invalid platform"}, 400


@app.route("/api/file", methods=["GET"])
def serve_file():
    """Sends file to frontend."""
    identifier = request.args.get("identifier")
    platform = request.args.get("platform")

    if platform == "youtube":
        return youtube_serve(identifier)
