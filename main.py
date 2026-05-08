import os
import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import  generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///cafe_aroma.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ------ Flask Log-in ----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "admin_login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))


# --- Classes ----------------- #
class Admin(UserMixin, db.Model):
    __tablename__ = "admins"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    email:Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

class Order(db.Model):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    item: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_time: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
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

# ---- Seed admin from .env -----------




if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", 8000))
    app.run(debug=debug, port=port)

