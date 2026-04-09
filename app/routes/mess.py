from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.entities import Menu, Vote
from app.routes.utils import parse_int, role_required

mess_bp = Blueprint("mess", __name__, url_prefix="/mess")


@mess_bp.route("/menu", methods=["GET", "POST"])
@login_required
def menu():
    day = request.args.get("day", "").strip()
    if current_user.role == "admin" and request.method == "POST":
        db.session.add(Menu(day=request.form.get("day", "Monday"), meal_type=request.form.get("meal_type", "Lunch"), item=request.form.get("item", "").strip()))
        db.session.commit()
        flash("Menu item added.", "success")
        return redirect(url_for("mess.menu"))
    query = Menu.query
    if day:
        query = query.filter_by(day=day)
    return render_template("mess/menu.html", items=query.order_by(Menu.day, Menu.meal_type).all(), day=day)


@mess_bp.route("/vote/<int:menu_id>", methods=["POST"])
@login_required
@role_required("student")
def vote(menu_id):
    menu = Menu.query.get_or_404(menu_id)
    rating = parse_int(request.form.get("rating"), default=3, min_value=1, max_value=5)
    existing = Vote.query.filter_by(menu_id=menu_id, student_id=current_user.id).first()
    if existing:
        existing.rating = rating
    else:
        db.session.add(Vote(menu_id=menu_id, student_id=current_user.id, rating=rating))
    db.session.commit()
    flash(f"Vote submitted for {menu.item}.", "success")
    return redirect(url_for("mess.menu"))


@mess_bp.route("/waste")
@login_required
def waste_tracking():
    return render_template("mess/waste.html", data={"Mon": 6, "Tue": 4, "Wed": 8, "Thu": 5, "Fri": 3, "Sat": 7, "Sun": 4})
