from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.models.entities import Bed, Complaint, Fee, Inventory, LostFoundItem, Outpass, Room, User
from app.routes.utils import parse_int, role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = {
        "students": User.query.filter_by(role="student").count(),
        "rooms": Room.query.count(),
        "open_complaints": Complaint.query.filter(Complaint.status != "Resolved").count(),
        "pending_outpasses": Outpass.query.filter_by(status="Pending").count(),
        "pending_fees": Fee.query.filter_by(status="Pending").count(),
    }
    chart_labels = ["Students", "Rooms", "Complaints", "Outpasses", "Fees"]
    chart_values = [stats["students"], stats["rooms"], stats["open_complaints"], stats["pending_outpasses"], stats["pending_fees"]]
    return render_template("admin/dashboard.html", stats=stats, chart_labels=chart_labels, chart_values=chart_values)


@admin_bp.route("/rooms", methods=["GET", "POST"])
@login_required
@role_required("admin")
def rooms():
    if request.method == "POST":
        floor = parse_int(request.form.get("floor"), default=1, min_value=1, max_value=30)
        capacity = parse_int(request.form.get("capacity"), default=3, min_value=1, max_value=10)
        room = Room(
            room_number=request.form.get("room_number", "").strip(),
            block=request.form.get("block", "A").strip(),
            floor=floor,
            capacity=capacity,
        )
        if not room.room_number:
            flash("Room number is required.", "danger")
            return redirect(url_for("admin.rooms"))
        db.session.add(room)
        try:
            db.session.flush()
            for i in range(room.capacity):
                db.session.add(Bed(label=f"Bed-{i + 1}", room_id=room.id))
            db.session.add(Inventory(item_name="Fan", quantity=1, room_id=room.id))
            db.session.add(Inventory(item_name="Table", quantity=1, room_id=room.id))
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Room number already exists.", "danger")
            return redirect(url_for("admin.rooms"))
        flash("Room added successfully.", "success")
        return redirect(url_for("admin.rooms"))

    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    query = Room.query
    if q:
        query = query.filter(Room.room_number.contains(q))
    pagination = query.order_by(Room.room_number).paginate(page=page, per_page=8, error_out=False)
    return render_template("admin/rooms.html", pagination=pagination, q=q)


@admin_bp.route("/rooms/<int:room_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    if room.residents:
        flash("Cannot delete occupied room.", "danger")
        return redirect(url_for("admin.rooms"))
    db.session.delete(room)
    db.session.commit()
    flash("Room deleted.", "info")
    return redirect(url_for("admin.rooms"))


@admin_bp.route("/assign-room", methods=["GET", "POST"])
@login_required
@role_required("admin")
def assign_room():
    students = User.query.filter_by(role="student").all()
    available_rooms = Room.query.all()

    if request.method == "POST":
        student_id = parse_int(request.form.get("student_id"))
        room_id = parse_int(request.form.get("room_id"))
        if not student_id or not room_id:
            flash("Please select valid student and room.", "danger")
            return redirect(url_for("admin.assign_room"))
        student = User.query.get_or_404(student_id)
        room = Room.query.get_or_404(room_id)
        if student.role != "student":
            flash("Only student records can be assigned to rooms.", "danger")
            return redirect(url_for("admin.assign_room"))
        if room.available <= 0:
            flash("No beds available in selected room.", "danger")
            return redirect(url_for("admin.assign_room"))
        # Free one bed from previous room on reassignment.
        if student.room_id and student.room_id != room.id:
            old_bed = Bed.query.filter_by(room_id=student.room_id, is_occupied=True).first()
            if old_bed:
                old_bed.is_occupied = False
        student.room_id = room.id
        bed = Bed.query.filter_by(room_id=room.id, is_occupied=False).first()
        if bed:
            bed.is_occupied = True
        db.session.commit()
        flash("Room assigned successfully.", "success")
        return redirect(url_for("admin.assign_room"))

    suggestions = []
    for student in students:
        if student.room_id:
            continue
        for room in available_rooms:
            if room.available <= 0:
                continue
            roommates = [u for u in room.residents if u.role == "student"]
            if roommates and any(r.branch == student.branch and r.year == student.year for r in roommates):
                suggestions.append((student, room))
                break

    return render_template("admin/assign_room.html", students=students, rooms=available_rooms, suggestions=suggestions)


@admin_bp.route("/analytics")
@login_required
@role_required("admin")
def analytics():
    status_counts = {
        "Open": Complaint.query.filter_by(status="Open").count(),
        "In Progress": Complaint.query.filter_by(status="In Progress").count(),
        "Resolved": Complaint.query.filter_by(status="Resolved").count(),
    }
    return render_template("admin/analytics.html", status_counts=status_counts, lost_found=LostFoundItem.query.count())
