from datetime import date
from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.entities import Outpass
from app.routes.utils import role_required

safety_bp = Blueprint("safety", __name__, url_prefix="/safety")


@safety_bp.route("/outpass", methods=["GET", "POST"])
@login_required
def outpass():
    status = request.args.get("status", "").strip()
    if current_user.role == "student" and request.method == "POST":
        reason = request.form.get("reason", "").strip()
        start_raw = request.form.get("date_from")
        end_raw = request.form.get("date_to")
        if not reason or not start_raw or not end_raw:
            flash("Please complete all out-pass fields.", "danger")
            return redirect(url_for("safety.outpass"))
        try:
            date_from = date.fromisoformat(start_raw)
            date_to = date.fromisoformat(end_raw)
        except ValueError:
            flash("Invalid out-pass dates.", "danger")
            return redirect(url_for("safety.outpass"))
        if date_to < date_from:
            flash("Return date cannot be before departure date.", "danger")
            return redirect(url_for("safety.outpass"))
        db.session.add(
            Outpass(
                student_id=current_user.id,
                reason=reason,
                date_from=date_from,
                date_to=date_to,
                qr_token=f"QR-{uuid4().hex[:10].upper()}",
            )
        )
        db.session.commit()
        flash("Out-pass request submitted.", "success")
        return redirect(url_for("safety.outpass"))
    if current_user.role == "admin":
        query = Outpass.query
    else:
        query = Outpass.query.filter_by(student_id=current_user.id)
    if status in {"Pending", "Approved", "Rejected"}:
        query = query.filter_by(status=status)
    records = query.order_by(Outpass.id.desc()).all()
    return render_template("safety/outpass.html", records=records, status=status)


@safety_bp.route("/outpass/<int:outpass_id>/<string:decision>", methods=["POST"])
@login_required
@role_required("admin")
def decide_outpass(outpass_id, decision):
    outpass_obj = Outpass.query.get_or_404(outpass_id)
    if decision not in {"approve", "reject"}:
        flash("Invalid action.", "danger")
        return redirect(url_for("safety.outpass"))
    outpass_obj.status = "Approved" if decision == "approve" else "Rejected"
    db.session.commit()
    flash(f"Out-pass {outpass_obj.status.lower()}.", "info")
    return redirect(url_for("safety.outpass"))


@safety_bp.route("/sos", methods=["GET", "POST"])
@login_required
def sos():
    if request.method == "POST":
        flash("SOS alert sent to rector/security (mock SMS).", "danger")
        return redirect(url_for("safety.sos"))
    return render_template("safety/sos.html")
