import json
import os
import datetime
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

# ── App ───────────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# ── Database ──────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///cafe_aroma.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ── Mail ──────────────────────────────────────────────────────────────────────

app.config["MAIL_SERVER"]   = os.getenv("MAIL_SERVER",   "smtp.gmail.com")
app.config["MAIL_PORT"]     = int(os.getenv("MAIL_PORT", "587"))
app.config["MAIL_USE_TLS"]  = os.getenv("MAIL_USE_TLS",  "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_SENDER", "Café Aroma 55 <noreply@cafearoma55.com>")
mail = Mail(app)

# ── Flask-Login ───────────────────────────────────────────────────────────────

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))

# ── Models ────────────────────────────────────────────────────────────────────

class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id:         Mapped[int] = mapped_column(Integer, primary_key=True)
    email:      Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password:   Mapped[str] = mapped_column(String(255), nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id:          Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:        Mapped[str] = mapped_column(String(255), nullable=False)
    phone:       Mapped[str] = mapped_column(String(50),  nullable=False)
    email:       Mapped[str] = mapped_column(String(255), nullable=True)
    item:        Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_time: Mapped[str] = mapped_column(String(20),  nullable=False)
    notes:       Mapped[str] = mapped_column(String(500), nullable=True)
    status:      Mapped[str] = mapped_column(String(20),  default="pending")
    hidden:      Mapped[bool] = mapped_column(Boolean,    default=False)
    created_at:  Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class Newsletter(db.Model):
    __tablename__ = "newsletter"
    id:         Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:      Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name:       Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class GelatoFlavor(db.Model):
    __tablename__ = "gelato"
    id:         Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flavors:    Mapped[str] = mapped_column(String(500), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class Review(db.Model):
    __tablename__ = "reviews"
    id:         Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author:     Mapped[str] = mapped_column(String(100), nullable=False)
    rating:     Mapped[int] = mapped_column(Integer, nullable=False)
    text:       Mapped[str] = mapped_column(String(600), nullable=False)
    status:     Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

# ── Seed admin from .env ──────────────────────────────────────────────────────

def seed_admin():
    email    = os.getenv("ADMIN_EMAIL",    "admin@cafearoma55.com")
    password = os.getenv("ADMIN_PASSWORD", "aroma2025")

    existing = db.session.execute(
        db.select(Admin).where(Admin.email == email)
    ).scalar_one_or_none()

    if not existing:
        db.session.add(Admin(
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        ))
        db.session.commit()

# ── Helpers ───────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent / "data"

def load_menu():
    with open(DATA_DIR / "menu.json", encoding="utf-8") as f:
        return json.load(f)

def load_info():
    with open(DATA_DIR / "info.json", encoding="utf-8") as f:
        return json.load(f)

def get_gelato():
    row = db.session.execute(
        db.select(GelatoFlavor).order_by(GelatoFlavor.id.desc())
    ).scalar_one_or_none()
    return row.flavors.split(",") if row else ["Pistachio", "Stracciatella", "Lemon Sorbet"]

# ── Context processor (injected into ALL templates) ───────────────────────────

@app.context_processor
def inject_globals():
    return {
        "now":   datetime.datetime.now(),
        "today": datetime.datetime.now().strftime("%A"),
        "info":  load_info(),
    }

# ── Init ──────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()
    seed_admin()

# ── Public routes ─────────────────────────────────────────────────────────────

@app.route("/")
def home():
    approved = db.session.execute(
        db.select(Review)
          .where(Review.status == "approved")
          .order_by(Review.created_at.desc())
    ).scalars().all()
    return render_template("index.html",
                           menu=load_menu(),
                           gelato=get_gelato(),
                           db_reviews=approved)


@app.route("/order", methods=["POST"])
def place_order():
    name        = request.form.get("name", "").strip()
    phone       = request.form.get("phone", "").strip()
    email       = request.form.get("email", "").strip() or None
    item        = request.form.get("item", "").strip()
    pickup_time = request.form.get("pickup_time", "").strip()
    notes       = request.form.get("notes", "").strip()

    if not all([name, phone, item, pickup_time]):
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("home") + "#order-modal")

    db.session.add(Order(name=name, phone=phone, email=email, item=item,
                         pickup_time=pickup_time, notes=notes))
    db.session.commit()
    flash(f"Order received! See you at {pickup_time}, {name}! ☕", "success")
    return redirect(url_for("home"))


@app.route("/review", methods=["POST"])
def submit_review():
    author     = request.form.get("author", "").strip()
    text       = request.form.get("text",   "").strip()
    rating_raw = request.form.get("rating", "").strip()

    if not all([author, text, rating_raw]):
        flash("Please fill in all fields.", "error")
        return redirect(url_for("home") + "#leave-review")

    try:
        rating = int(rating_raw)
        if not 1 <= rating <= 5:
            raise ValueError
    except ValueError:
        flash("Please select a star rating.", "error")
        return redirect(url_for("home") + "#leave-review")

    db.session.add(Review(author=author, rating=rating, text=text))
    db.session.commit()
    flash("Thank you! Your review will appear once approved. ☕", "success")
    return redirect(url_for("home") + "#reviews")


@app.route("/newsletter", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip()
    name  = request.form.get("name",  "").strip()

    if not email:
        flash("Email is required.", "error")
        return redirect(url_for("home") + "#newsletter")

    existing = db.session.execute(
        db.select(Newsletter).where(Newsletter.email == email)
    ).scalar_one_or_none()

    if existing:
        flash("This email is already subscribed.", "error")
    else:
        db.session.add(Newsletter(email=email, name=name))
        db.session.commit()
        flash("Welcome to the Café Aroma family! ☕", "success")

    return redirect(url_for("home"))

# ── Admin: login / logout ─────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        admin = db.session.execute(
            db.select(Admin).where(Admin.email == email)
        ).scalar_one_or_none()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for("admin_dashboard"))

        flash("Wrong email or password.", "error")
        return redirect(url_for("admin_login"))

    return render_template("admin_login.html")


@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for("admin_login"))

# ── Admin: dashboard ──────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
def admin_dashboard():
    all_orders  = db.session.execute(
        db.select(Order).order_by(Order.created_at.desc())
    ).scalars().all()

    orders = [o for o in all_orders if not o.hidden]

    subscribers = db.session.execute(
        db.select(Newsletter).order_by(Newsletter.created_at.desc())
    ).scalars().all()

    reviews = db.session.execute(
        db.select(Review).order_by(Review.created_at.desc())
    ).scalars().all()

    today_str        = datetime.date.today().isoformat()
    today_orders     = [o for o in all_orders if o.created_at.date().isoformat() == today_str]
    pending_orders   = [o for o in orders if o.status == "pending"]
    pending_reviews  = [r for r in reviews if r.status == "pending"]

    return render_template("admin.html",
                           orders=orders,
                           subscribers=subscribers,
                           reviews=reviews,
                           gelato_flavors=get_gelato(),
                           today_count=len(today_orders),
                           pending_count=len(pending_orders),
                           pending_reviews_count=len(pending_reviews))


@app.route("/admin/gelato", methods=["POST"])
@login_required
def update_gelato():
    flavors = [
        request.form.get(f"flavor_{i}", "").strip()
        for i in range(1, 5)
    ]
    flavors = [f for f in flavors if f]
    if flavors:
        db.session.add(GelatoFlavor(flavors=",".join(flavors)))
        db.session.commit()
        flash("Gelato flavors updated! 🍦", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/order/<int:order_id>/delete", methods=["POST"])
@login_required
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    order.hidden = True
    db.session.commit()
    flash(f"Order #{order_id} removed from panel.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/review/<int:review_id>/approve", methods=["POST"])
@login_required
def approve_review(review_id):
    review = db.session.get(Review, review_id)
    if not review:
        abort(404)
    review.status = "approved"
    db.session.commit()
    flash(f"Review by {review.author} approved. ✓", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/review/<int:review_id>/reject", methods=["POST"])
@login_required
def reject_review(review_id):
    review = db.session.get(Review, review_id)
    if not review:
        abort(404)
    db.session.delete(review)
    db.session.commit()
    flash("Review removed.", "success")
    return redirect(url_for("admin_dashboard"))


def send_ready_email(order):
    """Send a 'your order is ready' email to the customer."""
    if not order.email:
        return
    try:
        html = f"""
        <div style="font-family:'Georgia',serif;max-width:520px;margin:auto;
                    background:#1f1510;color:#f0e8d8;border-radius:12px;
                    overflow:hidden;border:1px solid rgba(196,145,58,.2)">
          <div style="background:linear-gradient(90deg,#c4913a,#d4a44a);
                      padding:28px 32px;text-align:center">
            <h1 style="margin:0;font-weight:300;font-size:26px;color:#1f1510;letter-spacing:.04em">
              Café Aroma 55
            </h1>
          </div>
          <div style="padding:32px">
            <p style="font-size:18px;color:#f0e8d8;margin:0 0 12px">
              Hey <strong>{order.name}</strong>! ☕
            </p>
            <p style="font-size:16px;color:#c4913a;font-weight:500;margin:0 0 24px">
              Your order is ready for pickup!
            </p>
            <div style="background:rgba(255,255,255,.04);border:1px solid rgba(196,145,58,.15);
                        border-radius:8px;padding:16px 20px;margin-bottom:24px">
              <p style="margin:0 0 6px;color:#94826a;font-size:12px;
                        text-transform:uppercase;letter-spacing:.1em">Your Order</p>
              <p style="margin:0;color:#f0e8d8;font-size:16px">{order.item}</p>
              <p style="margin:6px 0 0;color:#94826a;font-size:13px">
                Pickup time: <strong style="color:#f0e8d8">{order.pickup_time}</strong>
              </p>
            </div>
            <p style="color:#94826a;font-size:14px;margin:0">
              We're at <strong style="color:#f0e8d8">55 Wall St, Norwalk CT</strong>.
              See you soon!
            </p>
          </div>
          <div style="padding:16px 32px;border-top:1px solid rgba(196,145,58,.1);
                      text-align:center">
            <p style="margin:0;color:#5a4a38;font-size:12px">
              © Café Aroma 55 · (203) 354-0677
            </p>
          </div>
        </div>
        """
        msg = Message(
            subject="Your order is ready! ☕ — Café Aroma 55",
            recipients=[order.email],
            html=html
        )
        mail.send(msg)
    except Exception as e:
        app.logger.warning(f"Could not send ready email for order #{order.id}: {e}")


@app.route("/admin/order/<int:order_id>/<string:status>", methods=["POST"])
@login_required
def update_order(order_id, status):
    if status not in ("pending", "ready", "done"):
        abort(400)
    order = db.session.get(Order, order_id)
    if not order:
        abort(404)
    order.status = status
    db.session.commit()
    if status == "ready":
        send_ready_email(order)
    flash(f"Order #{order_id} marked as {status}.", "success")
    return redirect(url_for("admin_dashboard"))


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port  = int(os.getenv("PORT", 8000))
    app.run(debug=debug, port=port)