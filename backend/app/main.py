import os
import re
import logging
from datetime import timedelta

from flask import Flask, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from backend.app.services.memora_service import answer_query


# ============================================================
# 1. FLASK CONFIGURATION
# ============================================================

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "MEMORA_SECRET_KEY",
    "dev-only-change-this-before-deployment"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///memora_accounts.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Local development session settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Allow the React frontend to send session cookies.
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173"],
)


# ============================================================
# 2. DATABASE MODELS
# ============================================================

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(160),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    members = db.relationship(
        "User",
        backref="company",
        lazy=True
    )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(120),
        nullable=False
    )

    email = db.Column(
        db.String(254),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(128),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        nullable=False,
        default="admin"
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey("company.id"),
        nullable=False
    )


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================

def current_user():
    """Return the logged-in user from the session."""

    user_id = session.get("user_id")

    if not user_id:
        return None

    return db.session.get(User, user_id)


def user_response(user):
    """Return safe user details without the password hash."""

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "company": {
            "id": user.company.id,
            "name": user.company.name,
        },
    }


# Create database tables if they do not exist.
with app.app_context():
    db.create_all()


# ============================================================
# 4. HEALTH CHECK
# ============================================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "MEMORA"
    }), 200


# ============================================================
# 5. COMPANY REGISTRATION
# Registration does not automatically log the user in.
# ============================================================

@app.route("/auth/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    company_name = str(
        data.get("company_name", "")
    ).strip()

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = data.get("password", "")

    # Validate required fields
    if not all([name, company_name, email, password]):
        return jsonify({
            "error": "Please complete all required fields."
        }), 400

    # Validate lengths
    if len(name) > 120 or len(company_name) > 160:
        return jsonify({
            "error": "Name or company name is too long."
        }), 400

    # Validate email
    if (
        len(email) > 254
        or not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        )
    ):
        return jsonify({
            "error": "Please enter a valid email address."
        }), 400

    # Validate password
    if (
        not isinstance(password, str)
        or not 8 <= len(password.encode("utf-8")) <= 72
    ):
        return jsonify({
            "error": "Password must be between 8 and 72 bytes."
        }), 400

    # Prevent duplicate accounts
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": (
                "An account with this email already exists. "
                "Please log in."
            )
        }), 409

    try:
        # Create company
        company = Company(name=company_name)

        db.session.add(company)
        db.session.flush()

        # Hash password before saving
        password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        # Create company administrator
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role="admin",
            company_id=company.id
        )

        db.session.add(user)
        db.session.commit()

        # Important: do not create a login session here.
        return jsonify({
            "message": (
                "Company registered successfully. "
                "Please log in."
            ),
            "user": user_response(user)
        }), 201

    except Exception:
        db.session.rollback()

        app.logger.exception(
            "Company registration failed"
        )

        return jsonify({
            "error": "Registration failed. Please try again."
        }), 500


# ============================================================
# 6. LOGIN
# ============================================================

@app.route("/auth/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = str(
        data.get("email", "")
    ).strip().lower()

    password = data.get("password", "")

    user = User.query.filter_by(
        email=email
    ).first()

    # Validate credentials
    if (
        not user
        or not isinstance(password, str)
        or not bcrypt.check_password_hash(
            user.password_hash,
            password
        )
    ):
        return jsonify({
            "error": "Invalid email or password."
        }), 401

    # Clear any previous session
    session.clear()

    # Create a fresh authenticated session
    session.permanent = True
    session["user_id"] = user.id

    response = jsonify({
        "message": "Login successful.",
        "user": user_response(user)
    })

    return response, 200


# ============================================================
# 7. CHECK CURRENT LOGIN SESSION
# ============================================================

@app.route("/auth/me", methods=["GET"])
def me():

    user = current_user()

    if not user:
        return jsonify({
            "error": "Authentication required."
        }), 401

    return jsonify({
        "user": user_response(user)
    }), 200


# ============================================================
# 8. LOGOUT
# ============================================================

@app.route("/auth/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully."
    }), 200


# ============================================================
# 9. ASK MEMORA
# Requires an authenticated user.
# ============================================================

@app.route("/ask", methods=["POST"])
def ask():

    user = current_user()

    if not user:
        return jsonify({
            "error": "Please log in to use MEMORA."
        }), 401

    data = request.get_json(silent=True) or {}

    query = data.get("query", "")

    if not isinstance(query, str) or not query.strip():
        return jsonify({
            "error": "Query is required."
        }), 400

    try:
        result = answer_query(query.strip())

        return jsonify(result), 200

    except Exception:
        app.logger.exception(
            "MEMORA query failed"
        )

        return jsonify({
            "error": (
                "MEMORA could not complete the question. "
                "Please try again shortly."
            )
        }), 500


# ============================================================
# 10. START SERVER
# ============================================================

if __name__ == "__main__":

    # Debug mode is only for local development.
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )