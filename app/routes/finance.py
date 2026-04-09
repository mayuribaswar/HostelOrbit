from datetime import date
from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models.entities import Expense, Fee, Payment, User
from app.routes.utils import parse_float, parse_int, role_required

finance_bp = Blueprint("finance", __name__, url_prefix="/finance")


@finance_bp.route("/fees", methods=["GET", "POST"])
@login_required
def fees():
    status = request.args.get("status", "").strip()
    if current_user.role == "admin" and request.method == "POST":
        student_id = parse_int(request.form.get("student_id"))
        amount = parse_float(request.form.get("amount"), default=None, min_value=1)
        due_date_raw = request.form.get("due_date")
        if not student_id or amount is None or not due_date_raw:
            flash("Please provide valid fee data.", "danger")
            return redirect(url_for("finance.fees"))
        try:
            due_date = date.fromisoformat(due_date_raw)
        except ValueError:
            flash("Invalid due date.", "danger")
            return redirect(url_for("finance.fees"))
        fee = Fee(
            student_id=student_id,
            amount=amount,
            due_date=due_date,
            penalty=100.0 if due_date < date.today() else 0.0,
        )
        db.session.add(fee)
        db.session.commit()
        flash("Fee invoice generated.", "success")
        return redirect(url_for("finance.fees"))
    if current_user.role == "admin":
        query = Fee.query
        if status in {"Paid", "Pending"}:
            query = query.filter_by(status=status)
        return render_template("finance/fees.html", fee_records=query.order_by(Fee.created_at.desc()).all(), students=User.query.filter_by(role="student").all(), status=status)
    query = Fee.query.filter_by(student_id=current_user.id)
    if status in {"Paid", "Pending"}:
        query = query.filter_by(status=status)
    return render_template("finance/fees.html", fee_records=query.order_by(Fee.created_at.desc()).all(), students=[], status=status)


@finance_bp.route("/pay/<int:fee_id>", methods=["POST"])
@login_required
@role_required("student")
def pay_fee(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    if fee.student_id != current_user.id:
        flash("Invalid payment request.", "danger")
        return redirect(url_for("finance.fees"))
    if fee.status == "Paid":
        flash("This invoice is already paid.", "warning")
        return redirect(url_for("finance.fees"))
    payment = Payment(fee_id=fee.id, amount_paid=fee.amount + fee.penalty, method="UPI", txn_ref=f"SIM-UPI-{uuid4().hex[:8].upper()}")
    fee.status = "Paid"
    db.session.add(payment)
    db.session.commit()
    flash("Payment simulated successfully via UPI.", "success")
    return redirect(url_for("finance.fees"))


@finance_bp.route("/expenses", methods=["GET", "POST"])
@login_required
@role_required("admin")
def expenses():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        amount = parse_float(request.form.get("amount"), default=None, min_value=1)
        category = request.form.get("category", "Operations").strip()
        if not title or amount is None:
            flash("Please provide valid expense details.", "danger")
            return redirect(url_for("finance.expenses"))
        db.session.add(Expense(title=title, amount=amount, category=category))
        db.session.commit()
        flash("Expense recorded.", "success")
        return redirect(url_for("finance.expenses"))
    return render_template("finance/expenses.html", expenses=Expense.query.order_by(Expense.spent_on.desc()).all())
