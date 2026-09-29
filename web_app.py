"""
DataSense AI - Flask Web Backend
Upload CSV or Excel files and receive automatic data analysis.
Includes login and signup authentication.
"""

from __future__ import annotations

import json
import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from core.web_analysis import analyze_dataframe, apply_chat_instruction, load_dataframe


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "datasense-ai-local-dev-secret-2024")

LATEST_ANALYSIS = None

# ------------------------------------------------------------------ #
# Simple file-based user store (local dev - no DB required)
# ------------------------------------------------------------------ #
# Vercel's filesystem is read-only except /tmp (temporary, resets often)
if os.environ.get("VERCEL"):
    USERS_FILE = "/tmp/users.json"
else:
    USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load_users() -> dict:
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_users(users: dict) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ------------------------------------------------------------------ #
# Auth routes
# ------------------------------------------------------------------ #

@app.get("/login")
def login_page():
    if "user" in session:
        return redirect(url_for("index"))
    return render_template(
        "login.html",
        error=request.args.get("error"),
        success=request.args.get("success"),
    )


@app.post("/login")
def login_submit():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Please fill in all fields.")

    users = _load_users()
    user = users.get(email)

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html", error="Invalid email or password.")

    session["user"] = email
    session["name"] = user.get("name", email)
    return redirect(url_for("index"))


@app.get("/signup")
def signup_page():
    if "user" in session:
        return redirect(url_for("index"))
    return render_template("signup.html", error=request.args.get("error"))


@app.post("/signup")
def signup_submit():
    first_name = request.form.get("first_name", "").strip()
    last_name  = request.form.get("last_name", "").strip()
    email      = request.form.get("email", "").strip().lower()
    password   = request.form.get("password", "")
    confirm    = request.form.get("confirm_password", "")
    agree      = request.form.get("agree")

    if not all([first_name, last_name, email, password, confirm]):
        return render_template("signup.html", error="Please fill in all fields.")

    if password != confirm:
        return render_template("signup.html", error="Passwords do not match.")

    if len(password) < 8:
        return render_template("signup.html", error="Password must be at least 8 characters.")

    if not agree:
        return render_template("signup.html", error="You must agree to the Terms of Service.")

    users = _load_users()
    if email in users:
        return render_template("signup.html", error="An account with this email already exists.")

    users[email] = {
        "name": f"{first_name} {last_name}",
        "first_name": first_name,
        "last_name": last_name,
        "password_hash": generate_password_hash(password),
    }
    _save_users(users)

    return redirect(url_for("login_page") + "?success=Account+created!+Please+sign+in.")


@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# ------------------------------------------------------------------ #
# Dashboard / analysis routes (login required)
# ------------------------------------------------------------------ #

def _require_login():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return None


@app.get("/")
def index():
    redir = _require_login()
    if redir:
        return redir
    return render_template("index.html",
                           session_user=session.get("name", session.get("user")),
                           session_email=session.get("user"))


@app.post("/analyze")
def analyze_upload():
    redir = _require_login()
    if redir:
        return redir
    try:
        analysis = _analyze_request_file()
        return render_template("index.html", analysis=analysis,
                               session_user=session.get("name", session.get("user")),
                               session_email=session.get("user"))
    except ValueError as exc:
        return render_template("index.html", error=str(exc),
                               session_user=session.get("name", session.get("user")),
                               session_email=session.get("user")), 400


@app.post("/chat")
def chat_instruction():
    redir = _require_login()
    if redir:
        return redir
    try:
        analysis = _apply_instruction_to_latest()
        return render_template("index.html", analysis=analysis,
                               session_user=session.get("name", session.get("user")),
                               session_email=session.get("user"))
    except ValueError as exc:
        return render_template("index.html", error=str(exc),
                               session_user=session.get("name", session.get("user")),
                               session_email=session.get("user")), 400


@app.post("/api/analyze")
def analyze_upload_api():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        return jsonify(_analyze_request_file())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.post("/api/chat")
def chat_instruction_api():
    redir = _require_login()
    if redir:
        return jsonify({"error": "Not authenticated"}), 401
    try:
        return jsonify(_apply_instruction_to_latest())
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #

def _analyze_request_file():
    global LATEST_ANALYSIS
    uploaded_file = request.files.get("file")
    if uploaded_file is None or uploaded_file.filename == "":
        raise ValueError("Please choose a CSV or Excel file to upload.")
    filename = secure_filename(uploaded_file.filename or "uploaded-file")
    instruction = _get_instruction()
    df = load_dataframe(uploaded_file)
    LATEST_ANALYSIS = analyze_dataframe(df, filename=filename)
    return apply_chat_instruction(LATEST_ANALYSIS, instruction)


def _apply_instruction_to_latest():
    if LATEST_ANALYSIS is None:
        raise ValueError("Please upload and analyze a file before using the chatbot.")
    return apply_chat_instruction(LATEST_ANALYSIS, _get_instruction())


def _get_instruction():
    if request.is_json:
        data = request.get_json(silent=True) or {}
        return data.get("instruction", "")
    return request.form.get("instruction", "")


if __name__ == "__main__":
    app.run(debug=True)
