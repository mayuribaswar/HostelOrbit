from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.entities import LostFoundItem, MarketplaceItem, Room
from app.routes.utils import parse_float, role_required

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    return render_template("student/dashboard.html", room=current_user.room)


@student_bp.route("/room")
@login_required
@role_required("student")
def my_room():
    room = Room.query.get(current_user.room_id) if current_user.room_id else None
    return render_template("student/my_room.html", room=room)


@student_bp.route("/marketplace", methods=["GET", "POST"])
@login_required
@role_required("student")
def marketplace():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price = parse_float(request.form.get("price"), default=None, min_value=1)
        if not title or not description or price is None:
            flash("Please provide valid title, description, and price.", "danger")
            return redirect(url_for("student.marketplace"))
        item = MarketplaceItem(
            title=title,
            description=description,
            price=price,
            seller_id=current_user.id,
        )
        db.session.add(item)
        db.session.commit()
        flash("Item listed successfully.", "success")
        return redirect(url_for("student.marketplace"))

    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = MarketplaceItem.query.filter_by(status="Available")
    if q:
        query = query.filter(MarketplaceItem.title.contains(q))
    pagination = query.order_by(MarketplaceItem.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
    return render_template("student/marketplace.html", pagination=pagination, q=q)


@student_bp.route("/lost-found", methods=["GET", "POST"])
@login_required
@role_required("student")
def lost_found():
    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        if not item_name or not description or not location:
            flash("Please fill all lost & found fields.", "danger")
            return redirect(url_for("student.lost_found"))
        entry = LostFoundItem(
            item_name=item_name,
            description=description,
            location=location,
            reporter_id=current_user.id,
        )
        db.session.add(entry)
        db.session.commit()
        flash("Entry submitted.", "success")
        return redirect(url_for("student.lost_found"))
    return render_template("student/lost_found.html", items=LostFoundItem.query.order_by(LostFoundItem.created_at.desc()).all())
