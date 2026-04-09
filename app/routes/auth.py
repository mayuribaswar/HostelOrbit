from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.models.entities import User
from app.routes.utils import parse_int

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "student")
        hostel_id = request.form.get("hostel_id", "").strip()
        branch = request.form.get("branch", "General").strip()
        year = parse_int(request.form.get("year"), default=1, min_value=1, max_value=6)

        if not all([name, email, password, role, hostel_id]) or role not in {"student", "admin"}:
            flash("All required fields must be filled.", "danger")
            return render_template("auth/register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/register.html")

        if User.query.filter((User.email == email) | (User.hostel_id == hostel_id)).first():
            flash("Email or Hostel ID already exists.", "danger")
            return render_template("auth/register.html")

        user = User(name=name, email=email, role=role, hostel_id=hostel_id, branch=branch, year=year)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid credentials.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        flash("Welcome back!", "success")
        if user.role == "admin":
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("student.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))
