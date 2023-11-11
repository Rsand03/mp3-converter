"""Main application file"""
import re
import sqlite3
import bcrypt
from flask import Flask, Response, request
from backend.db import execute
from backend.token import create_token

app = Flask(__name__)


@app.route("/api/signup")
def signup():
    """
    Signup route. Creates a new user in the database.

    If the user is created successfully, returns a 200 status code and jwt token.
    If there is an error, returns a 400 status code and an error message.
    """
    email = request.args.get("email")
    password = request.args.get("password")
    password_confirm = request.args.get("password_confirm")

    if not email:
        return Response("Email is required", status=400)

    if not password:
        return Response("Password is required", status=400)

    if password != password_confirm:
        return Response("Passwords do not match", status=400)

    # test email with regex
    email_regex = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"

    if not re.match(email_regex, email):
        return Response("Email is invalid", status=400)

    # password must be at least 8 characters long
    if len(password) < 8:
        return Response("Password must be at least 8 characters long", status=400)

    # if email is already in use
    if execute("SELECT * FROM users WHERE email = ?", (email,)):
        return Response("Email is already in use", status=400)

    # crete a name for user based on email
    name = email.split("@")[0]
    default_motd = "Hello, World!"

    # hashing password
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    # insert user into database
    try:
        execute(
            "INSERT INTO users (name, email, password, motd) VALUES (?, ?, ?, ?)",
            (name, email, hashed_pw, default_motd),
        )
    except sqlite3.Error as e:
        return Response(f"An error occurred: {e}", status=500)

    # get user id
    user_id = execute("SELECT id FROM users WHERE email = ?", (email,))[0][0]

    # issue a jwt token for user
    token = create_token(user_id)
    return Response(token, status=200)


@app.route("/api/login")
def login():
    """
    Login route. Checks if the user exists and if the password is correct.

    If the user exists and the password is correct, returns a 200 status code and jwt token.
    """
    email = request.args.get("email")
    password = request.args.get("password")

    # check if email and password are provided
    if not email or not password:
        return Response("Email and password are required", status=400)

    # check if user exists
    user = execute("SELECT * FROM users WHERE email = ?", (email,))
    if not user:
        return Response("User does not exist", status=400)

    # check if password is correct
    hashed_pw = execute("SELECT password FROM users WHERE email = ?", (email,))[0][0]
    if not bcrypt.checkpw(password.encode(), hashed_pw):
        return Response("Password is incorrect", status=400)

    # making jwt token:
    user_id = execute("SELECT id FROM users WHERE email = ?", (email,))[0][0]
    token = create_token(user_id)
    return Response(token, status=200)
