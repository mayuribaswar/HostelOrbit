from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.entities import Complaint
from app.routes.utils import role_required

complaints_bp = Blueprint("complaints", __name__, url_prefix="/complaints")


@complaints_bp.route("/", methods=["GET", "POST"])
@login_required
def list_complaints():
    if current_user.role == "student" and request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Please complete complaint form.", "danger")
            return redirect(url_for("complaints.list_complaints"))
        db.session.add(Complaint(student_id=current_user.id, title=title, description=description))
        db.session.commit()
        flash("Complaint raised successfully.", "success")
        return redirect(url_for("complaints.list_complaints"))

    status = request.args.get("status", "")
    query = Complaint.query if current_user.role == "admin" else Complaint.query.filter_by(student_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    return render_template("complaints/list.html", complaints=query.order_by(Complaint.created_at.desc()).all(), status=status)


@complaints_bp.route("/<int:complaint_id>/update", methods=["POST"])
@login_required
@role_required("admin")
def update_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.vendor = request.form.get("vendor", "Unassigned").strip()
    status = request.form.get("status", complaint.status)
    if status not in {"Open", "In Progress", "Resolved"}:
        flash("Invalid complaint status.", "danger")
        return redirect(url_for("complaints.list_complaints"))
    complaint.status = status
    db.session.commit()
    flash("Ticket updated.", "success")
    return redirect(url_for("complaints.list_complaints"))
